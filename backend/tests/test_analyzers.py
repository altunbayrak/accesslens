from app.analyzers import header_findings, seo_findings
def test_seo_detects_missing_metadata():
    result = seo_findings("<html><body>hello</body></html>", "https://example.com")
    assert {x["title"] for x in result} >= {"Missing page title", "Missing meta description"}
def test_headers_detect_missing_protection():
    assert any(x["title"] == "Missing HSTS" for x in header_findings({}, "https://example.com"))
