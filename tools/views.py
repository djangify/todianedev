# tools/views.py
#
# Ported from the Djangify self-hosted eCommerce Site Builder's "tools" app.
# A free tool always shows its results in the browser. Two optional,
# non-gating extras sit alongside it:
#   1. A floating "Download PDF" button (print-to-PDF with branded attribution).
#   2. "Save to my dashboard" for a logged-in visitor, via the sandboxed
#      iframe -> parent page -> server postMessage relay (see tool_detail.html).
import json
import logging
import re

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.html import strip_tags
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.http import require_POST

from .models import (
    MAX_SAVED_RESULT_DATA_BYTES,
    MAX_SAVED_RESULTS_PER_TOOL,
    HostedTool,
    SavedToolResult,
)

logger = logging.getLogger("tools")

# Cap on the size of the results snapshot we accept from the browser, so a
# runaway tool can't post megabytes of markup at us.
MAX_RESULTS_HTML_BYTES = 200_000
MAX_RESULTS_TEXT_BYTES = 100_000


def _staff_preview(request):
    return request.GET.get("preview") == "1" and request.user.is_staff


# ---------------------------------------------------------------------------
# Download PDF button + branded attribution page
# ---------------------------------------------------------------------------

# Anchor tags that carry a real, followable link. We deliberately keep this to
# http(s) and mailto so we surface the kind of link a tool author puts on a
# "button", and skip in-page anchors (#...), javascript: handlers and relative
# paths that mean nothing once the page is a saved PDF.
_ANCHOR_RE = re.compile(
    r'<a\b[^>]*\bhref\s*=\s*(["\'])(?P<href>.*?)\1[^>]*>(?P<label>.*?)</a>',
    re.IGNORECASE | re.DOTALL,
)
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_MAX_HARVESTED_LINKS = 25


def _harvest_tool_links(html_bytes):
    """
    Pull followable links out of an uploaded artifact so they can be reprinted
    as plain "label — URL" text on the PDF attribution page.

    A tool author often adds a "button" that is really an <a href="..."> link.
    In a saved/printed PDF that button loses its destination, so here we scan
    the raw artifact HTML, collect each external link's visible text + URL,
    de-duplicate by URL and cap the count. Returns a list of (label, url)
    tuples (raw/unescaped — the caller escapes them).

    NOTE: this only sees real <a href> links. A <button onclick="location=...">
    style button hides its URL inside JavaScript and is not harvested.
    """
    try:
        html = html_bytes.decode("utf-8", "ignore")
    except Exception:
        return []

    seen = set()
    links = []
    for m in _ANCHOR_RE.finditer(html):
        href = (m.group("href") or "").strip()
        low = href.lower()
        if not (low.startswith("http://") or low.startswith("https://") or low.startswith("mailto:")):
            continue
        if href in seen:
            continue
        seen.add(href)
        label = _WS_RE.sub(" ", _TAG_RE.sub("", m.group("label") or "")).strip()
        if not label:
            label = href
        links.append((label, href))
        if len(links) >= _MAX_HARVESTED_LINKS:
            break
    return links


def _build_pdf_branding(links=None):
    """
    Build the HTML injected into every served hosted tool to give visitors a
    "Download PDF" button plus a branded attribution page.

    - On screen: only a small floating "Download PDF" button is visible.
    - When the visitor saves/prints to PDF: the button is hidden and a clean
      final page is appended carrying this site's identity (name, author,
      bio, URL) so they always remember where the PDF came from.

    Brand details come from Django settings (SITE_NAME / AUTHOR_*), so a
    missing value never breaks the tool — the button always renders and the
    attribution block only includes the pieces that are available.
    """
    from django.conf import settings
    from django.utils.html import escape

    business = escape((getattr(settings, "SITE_NAME", "") or "").strip())
    author = escape((getattr(settings, "AUTHOR_NAME", "") or "").strip())
    bio = escape((getattr(settings, "AUTHOR_SHORT_BIO", "") or "").strip())
    url = (getattr(settings, "SITE_URL", "") or "").strip()
    author_url = (getattr(settings, "AUTHOR_URL", "") or "").strip()
    url_safe = escape(url)

    # AUTHOR_URL is stored as a path (e.g. "/diane-corriette"); make it absolute.
    if author_url.startswith("/") and url:
        about_safe = escape(url.rstrip("/") + author_url)
    else:
        about_safe = escape(author_url)

    parts = ['<section class="tool-pdf-attribution">', '<div class="tool-pdf-rule"></div>']
    if business:
        parts.append('<p class="biz">' + business + "</p>")
    if author:
        parts.append("<h2>Created by " + author + "</h2>")
    if bio:
        parts.append("<p>" + bio + "</p>")
    meta = []
    if url:
        meta.append('<a href="' + url_safe + '">' + url_safe + "</a>")
    if about_safe:
        meta.append('<a href="' + about_safe + '">About</a>')
    if meta:
        parts.append('<p class="meta">' + " &nbsp;&bull;&nbsp; ".join(meta) + "</p>")
    if links:
        parts.append('<div class="tool-pdf-links">')
        parts.append('<p class="links-title">Links referenced in this tool</p>')
        parts.append("<ul>")
        for label, link_url in links:
            parts.append(
                '<li><span class="lbl">' + escape(label) + "</span><br>"
                '<a href="' + escape(link_url) + '">' + escape(link_url) + "</a></li>"
            )
        parts.append("</ul></div>")
    source = business or url_safe or getattr(settings, "SITE_NAME", "our site")
    parts.append(
        '<p class="meta">You received this from ' + source + ". Thank you for your support.</p>"
    )
    parts.append("</section>")
    attribution = "".join(parts)

    style = (
        '<style id="tool-pdf-style">'
        "@media screen{"
        ".tool-pdf-attribution{display:none;}"
        ".tool-pdf-btn{position:fixed;right:16px;bottom:16px;z-index:2147483647;"
        "font:600 14px/1 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;"
        "padding:11px 18px;background:#0f766e;color:#fff;border:0;border-radius:9999px;"
        "box-shadow:0 3px 10px rgba(0,0,0,.25);cursor:pointer;}"
        ".tool-pdf-btn:hover{background:#134e4a;}"
        "}"
        "@media print{"
        ".tool-pdf-btn{display:none !important;}"
        ".tool-pdf-attribution{display:block !important;page-break-before:always;"
        "break-before:page;font-family:Georgia,'Times New Roman',serif;color:#111;"
        "padding:56px 40px;}"
        ".tool-pdf-attribution .tool-pdf-rule{height:3px;width:64px;background:#0f766e;"
        "margin:0 0 22px;}"
        ".tool-pdf-attribution .biz{font-size:13px;letter-spacing:.08em;"
        "text-transform:uppercase;color:#555;margin:0 0 6px;}"
        ".tool-pdf-attribution h2{font-size:22px;margin:0 0 14px;}"
        ".tool-pdf-attribution p{font-size:13px;line-height:1.6;margin:0 0 12px;"
        "max-width:540px;}"
        ".tool-pdf-attribution a{color:#0f766e;text-decoration:none;}"
        ".tool-pdf-attribution .meta{font-size:12px;color:#555;}"
        ".tool-pdf-attribution .tool-pdf-links{margin:22px 0 0;}"
        ".tool-pdf-attribution .tool-pdf-links .links-title{font-size:13px;"
        "letter-spacing:.06em;text-transform:uppercase;color:#555;margin:0 0 10px;}"
        ".tool-pdf-attribution .tool-pdf-links ul{list-style:none;padding:0;margin:0;}"
        ".tool-pdf-attribution .tool-pdf-links li{margin:0 0 11px;font-size:13px;"
        "line-height:1.5;word-break:break-all;}"
        ".tool-pdf-attribution .tool-pdf-links .lbl{font-weight:bold;color:#111;}"
        "}"
        "</style>"
    )
    button = (
        '<button class="tool-pdf-btn" type="button" onclick="window.print()" '
        'aria-label="Download this as a PDF">&#8595; Download PDF</button>'
    )
    return style + button + attribution


# ---------------------------------------------------------------------------
# Results capture (for the "download PDF" print view and the save-to-
# dashboard flow)
#
# The tool renders in a sandboxed iframe with NO allow-same-origin, so its JS
# runs in an opaque origin the parent can't read. This tiny script lives inside
# the iframe and, when the parent asks (postMessage), snapshots the tool's
# current results and posts them back up.
# ---------------------------------------------------------------------------
_CAPTURE_SCRIPT = b"""<script>(function(){
  function findOutputRoot(root){
    var el = root.querySelector('[data-tool-output]');
    if (el) return el;
    var selectors = ['#tool-output','#tool-results','.tool-output','.tool-results','#results','#output'];
    for (var i=0;i<selectors.length;i++){
      el = root.querySelector(selectors[i]);
      if (el) return el;
    }
    return null;
  }
  function snapshot(){
    var live=document.querySelectorAll('input,textarea,select');
    var clone=document.body.cloneNode(true);
    var copy=clone.querySelectorAll('input,textarea,select');
    for(var i=0;i<live.length&&i<copy.length;i++){
      var l=live[i],c=copy[i];
      try{
        if(l.tagName==='SELECT'){
          if(c.options&&c.options[l.selectedIndex]){c.options[l.selectedIndex].setAttribute('selected','selected');}
        }else if(l.type==='checkbox'||l.type==='radio'){
          if(l.checked){c.setAttribute('checked','checked');}else{c.removeAttribute('checked');}
        }else if(l.tagName==='TEXTAREA'){
          c.textContent=l.value;
        }else{
          c.setAttribute('value',l.value);
        }
      }catch(e){}
    }
    var junk=clone.querySelectorAll('script,style,noscript,.tool-pdf-btn,.tool-pdf-attribution,.tool-pdf-style');
    for(var j=0;j<junk.length;j++){junk[j].parentNode&&junk[j].parentNode.removeChild(junk[j]);}
    var outputEl = findOutputRoot(clone);
    var liveOutputEl = outputEl ? findOutputRoot(document) : null;
    var html = outputEl ? outputEl.innerHTML : clone.innerHTML;
    var text = (liveOutputEl ? liveOutputEl.innerText : (document.body.innerText||'')).replace(/\\n{3,}/g,'\\n\\n').trim();
    return {html:html,text:text};
  }
  window.addEventListener('message',function(e){
    var d=e.data||{};
    if(d&&d.__toolCaptureRequest){
      var s=snapshot();
      parent.postMessage({__toolResults:{id:d.__toolCaptureRequest,html:s.html,text:s.text}},'*');
    }
  });
})();</script>"""


def tool_list(request):
    """
    Public index of all live tools (free and paid).

    Paid tools only appear here once they're linked to a sellable product —
    otherwise a visitor would have nothing to buy. When a paid tool IS linked,
    its card sends visitors straight to the product page (not the tool's own
    paywalled page), since that's where they actually complete the purchase.
    """
    visible_tools = []
    for tool in HostedTool.objects.filter(published=True):
        if not tool.is_visible_on_list:
            continue
        if tool.access == HostedTool.ACCESS_PAID:
            product = tool.get_sale_product()
            tool.list_product = product
            tool.list_url = product.get_absolute_url()
            tool.list_image_url = tool.image.url if tool.image else product.get_image_url()
            tool.list_description = strip_tags(tool.description) or strip_tags(product.description or "")
        else:
            tool.list_product = None
            tool.list_url = tool.get_absolute_url()
            tool.list_image_url = tool.image.url if tool.image else None
            tool.list_description = strip_tags(tool.description)
        visible_tools.append(tool)

    context = {"tools": visible_tools}
    return render(request, "tools/tool_list.html", context)


def _saving_enabled(tool):
    """Whether the "Save to my dashboard" button should be offered for this
    tool at all — both the site-wide switch and this tool's own switch must
    be on. Does not depend on whether the visitor is logged in; that's a
    separate concern handled in the template/JS."""
    if not tool.allow_saving:
        return False
    try:
        from shop.models import SiteSettings

        s = SiteSettings.get_settings()
    except Exception:
        s = None
    return bool(s is None or getattr(s, "tools_saving_enabled", True))


def _newsletter_box_context(request, tool, unlocked):
    """Whether (and with what copy) to show the opt-in "email me my results"
    box under a tool. Only free, unlocked tools qualify, only when the owner
    has turned the feature on in Site Settings, and only for logged-out
    visitors — a signed-in visitor gets the "save to dashboard" box instead."""
    if not (unlocked and tool.access == HostedTool.ACCESS_FREE):
        return {"show_newsletter_box": False}
    if request.user.is_authenticated:
        return {"show_newsletter_box": False}
    try:
        from shop.models import SiteSettings

        s = SiteSettings.get_settings()
    except Exception:
        s = None
    if not (s and getattr(s, "tools_newsletter_enabled", False)):
        return {"show_newsletter_box": False}
    return {
        "show_newsletter_box": True,
        "newsletter_title": (s.tools_newsletter_title or "").strip() or "Get your results by email",
        "newsletter_message": (s.tools_newsletter_message or "").strip(),
    }


def _tool_meta_description(tool):
    """Plain-text meta description for a tool's page."""
    raw = strip_tags(tool.description or "").strip() or strip_tags(tool.more_info_description or "").strip()
    text = " ".join(raw.split())
    if not text:
        return tool.title
    if len(text) > 160:
        text = text[:157].rstrip() + "..."
    return text


def tool_detail(request, slug):
    """
    Public wrapper page for a single tool. Shows site chrome (nav/footer) and
    embeds the artifact in a sandboxed iframe pointing at the raw view below.
    """
    if _staff_preview(request):
        tool = get_object_or_404(HostedTool, slug=slug)
    else:
        tool = get_object_or_404(HostedTool, slug=slug, published=True)

    unlocked = tool.is_unlocked_for(request.user)
    context = {
        "tool": tool,
        "unlocked": unlocked,
        "show_save_box": unlocked and _saving_enabled(tool),
        "meta_description": _tool_meta_description(tool),
    }
    if not unlocked:
        context["product"] = tool.get_sale_product()
    context.update(_newsletter_box_context(request, tool, unlocked))
    return render(request, "tools/tool_detail.html", context)


@xframe_options_sameorigin
def tool_raw(request, slug):
    """
    Serve the raw artifact HTML so its JavaScript executes.

    Security model:
      - The file lives in SecureStorage, so it is not directly web-served;
        this view is the only way to reach it.
      - It is only ever loaded inside the sandboxed iframe on the detail page
        (sandbox WITHOUT allow-same-origin => opaque origin => the artifact
        cannot read this site's cookies, session or DOM).
      - X-Frame-Options: SAMEORIGIN (decorator) lets our own page frame it
        while blocking other sites; frame-ancestors 'self' is the modern
        equivalent / belt-and-braces.
    """
    if _staff_preview(request):
        tool = get_object_or_404(HostedTool, slug=slug)
    else:
        tool = get_object_or_404(HostedTool, slug=slug, published=True)

    if not tool.is_unlocked_for(request.user):
        raise Http404("This tool requires purchase.")

    if not tool.html_file:
        raise Http404("No file attached to this tool.")

    try:
        with tool.html_file.open("rb") as fh:
            html = fh.read()
    except (FileNotFoundError, ValueError):
        raise Http404("Tool file missing on server.")

    reporter = (
        b"<script>(function(){"
        b"var t;"
        b"function measure(){var h=Math.max("
        b"document.body?document.body.scrollHeight:0,"
        b"document.documentElement?document.documentElement.scrollHeight:0);"
        b"parent.postMessage({__toolHeight:h},'*');}"
        b"function r(){clearTimeout(t);t=setTimeout(measure,60);}"
        b"window.addEventListener('load',r);"
        b"window.addEventListener('resize',r);"
        b"if(window.ResizeObserver){var ro=new ResizeObserver(r);"
        b"if(document.body){ro.observe(document.body);}}"
        b"if(window.MutationObserver){new MutationObserver(r).observe("
        b"document.documentElement,{childList:true,subtree:true,attributes:true});}"
        b"document.addEventListener('click',function(){setTimeout(r,60);setTimeout(r,450);});"
        b"setTimeout(r,300);setTimeout(r,1200);"
        b"})();</script>"
    )

    tool_links = _harvest_tool_links(html)
    if tool.link_text and tool.link_url:
        tool_links = [(tool.link_text, tool.link_url)] + [
            link for link in tool_links if link[1] != tool.link_url
        ]
    branding = _build_pdf_branding(tool_links).encode("utf-8")

    injected = reporter + _CAPTURE_SCRIPT + branding

    if b"</body>" in html:
        head, sep, tail = html.rpartition(b"</body>")
        html = head + injected + sep + tail
    else:
        html = html + injected

    response = HttpResponse(html, content_type="text/html; charset=utf-8")
    response["Content-Security-Policy"] = "frame-ancestors 'self'"
    response["X-Content-Type-Options"] = "nosniff"
    return response


# ---------------------------------------------------------------------------
# Sanitising a browser-supplied results snapshot (shared by both flows below)
# ---------------------------------------------------------------------------

def _sanitize_results_html(raw):
    """Light defence-in-depth on the snapshot the browser sends back. The
    content is this site's own tool, only ever shown back to the person who
    produced it, so this just strips things that have no place in saved
    output: <script>/<style> blocks, inline event handlers and javascript:
    URLs."""
    if not raw:
        return ""
    html = raw[:MAX_RESULTS_HTML_BYTES]
    html = re.sub(r"(?is)<script\b.*?</script>", "", html)
    html = re.sub(r"(?is)<style\b.*?</style>", "", html)
    html = re.sub(r"(?is)<noscript\b.*?</noscript>", "", html)
    html = re.sub(r"(?is)\son\w+\s*=\s*\"[^\"]*\"", "", html)
    html = re.sub(r"(?is)\son\w+\s*=\s*'[^']*'", "", html)
    html = re.sub(r"(?is)(href|src)\s*=\s*\"\s*javascript:[^\"]*\"", r'\1="#"', html)
    html = re.sub(r"(?is)(href|src)\s*=\s*'\s*javascript:[^']*'", r"\1='#'", html)
    return html


# ---------------------------------------------------------------------------
# "Email me my results" — the opt-in box under a free tool for logged-out
# visitors. This project has no connected email-marketing platform, so
# unlike the self-hosted version this only sends the email; it does not
# subscribe the visitor to a mailing list.
# ---------------------------------------------------------------------------

def _send_results_email(tool, name, to_email, results_html, results_text):
    from django.conf import settings as dj_settings
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string

    context = {
        "tool": tool,
        "name": name,
        "results_html": results_html,
        "results_text": results_text,
        "site_name": getattr(dj_settings, "SITE_NAME", ""),
    }
    html_body = render_to_string("tools/email/tool_results.html", context)
    text_body = (results_text or "").strip() or strip_tags(html_body)
    business = getattr(dj_settings, "SITE_NAME", "") or "our site"
    text_body = f"Here are your results from {tool.title}.\n\n{text_body}\n\nSent by {business}."

    subject = f"Your results from {tool.title}"
    msg = EmailMultiAlternatives(
        subject, text_body, dj_settings.DEFAULT_FROM_EMAIL, [to_email]
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()


@require_POST
def email_results(request, slug):
    """
    Handle the "email me my results" box under a free tool. Results are
    always shown on screen anyway, so this only runs when someone actively
    opts in.
    """
    if _staff_preview(request):
        tool = get_object_or_404(HostedTool, slug=slug)
    else:
        tool = get_object_or_404(HostedTool, slug=slug, published=True)

    if tool.access != HostedTool.ACCESS_FREE:
        raise Http404()
    try:
        from shop.models import SiteSettings

        s = SiteSettings.get_settings()
    except Exception:
        s = None
    if not (s and getattr(s, "tools_newsletter_enabled", False)):
        raise Http404()

    email = (request.POST.get("email") or "").strip()
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse(
            {"ok": False, "error": "Please enter a valid email address."}, status=400
        )
    name = (request.POST.get("name") or "").strip()[:120]
    results_html = _sanitize_results_html(request.POST.get("results_html") or "")
    results_text = (request.POST.get("results_text") or "")[:MAX_RESULTS_TEXT_BYTES]

    try:
        _send_results_email(tool, name, email, results_html, results_text)
    except Exception as exc:
        logger.error("Failed to email tool results to %s: %s", email, exc, exc_info=True)
        return JsonResponse(
            {"ok": False, "error": "We couldn't send the email just now. Please try again shortly."},
            status=502,
        )

    return JsonResponse({"ok": True, "message": "Sent! Check your inbox for your results."})


# ---------------------------------------------------------------------------
# Save to dashboard: persist a results snapshot to the visitor's own account
#
# Reuses the same iframe -> parent -> server path as email_results above: the
# sandboxed tool has no way to reach this endpoint itself (opaque origin, no
# allow-same-origin), so the parent page (tool_detail.html) is what asks the
# iframe for a snapshot via postMessage and POSTs it here on the visitor's
# behalf, with their real session.
# ---------------------------------------------------------------------------

@login_required
@require_POST
def save_result(request, slug):
    """
    Save a snapshot of a tool's results to request.user's dashboard.

    Expects POST body (form-encoded, matching email_results' shape):
        label         - required, short name the visitor sees on their dashboard
        results_html  - optional, sanitised the same way email_results() sanitises it
        results_text  - optional
        data          - optional, JSON string; only meaningful for a tool that
                        cooperates via the __toolSave postMessage contract

    Returns 200 {"ok": true, "id": <pk>} or 4xx {"ok": false, "error": "..."}.
    """
    if _staff_preview(request):
        tool = get_object_or_404(HostedTool, slug=slug)
    else:
        tool = get_object_or_404(HostedTool, slug=slug, published=True)

    if not _saving_enabled(tool):
        raise Http404()

    if not tool.is_unlocked_for(request.user):
        return JsonResponse(
            {"ok": False, "error": "You don't have access to this tool."}, status=403
        )

    label = (request.POST.get("label") or "").strip()[:300]
    if not label:
        return JsonResponse({"ok": False, "error": "label is required."}, status=400)

    results_html = _sanitize_results_html(request.POST.get("results_html") or "")
    results_text = (request.POST.get("results_text") or "")[:MAX_RESULTS_TEXT_BYTES]

    data = {}
    raw_data = request.POST.get("data")
    if raw_data:
        if len(raw_data.encode("utf-8")) > MAX_SAVED_RESULT_DATA_BYTES:
            return JsonResponse({"ok": False, "error": "That result is too large to save."}, status=400)
        try:
            parsed = json.loads(raw_data)
        except (json.JSONDecodeError, ValueError):
            parsed = None
        if isinstance(parsed, dict):
            data = parsed

    if not (label and (results_html or results_text or data)):
        return JsonResponse({"ok": False, "error": "Nothing to save."}, status=400)

    existing = SavedToolResult.objects.filter(user=request.user, tool=tool).count()
    if existing >= MAX_SAVED_RESULTS_PER_TOOL:
        return JsonResponse(
            {
                "ok": False,
                "error": (
                    f"You've saved the maximum of {MAX_SAVED_RESULTS_PER_TOOL} results "
                    "for this tool. Delete an old one from your dashboard first."
                ),
            },
            status=400,
        )

    result = SavedToolResult.objects.create(
        user=request.user,
        tool=tool,
        tool_title=tool.title,
        tool_slug=tool.slug,
        label=label,
        data=data,
        results_html=results_html,
        results_text=results_text,
    )
    return JsonResponse({"ok": True, "id": result.pk})
