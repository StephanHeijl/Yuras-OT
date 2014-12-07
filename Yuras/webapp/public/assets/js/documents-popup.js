$(function() {
	$("a.document-link").click(function(e) {
		e.preventDefault();
		window.open($(this).attr("href"), "", "width=1280, height=720");
	})
})