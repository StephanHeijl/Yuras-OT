$("a[data-to]").click(function (e) {
	e.preventDefault();

	// Scroll to element with data-target.
	var to = $(this).data("to"),
		target = $("*[data-target=" + to + "]");

	$("body,html").animate({
		scrollTop: target.offset().top - $(".navbar").height()
	})

	$(this).parents("ul").find(".active").removeClass("active")
	$(this).parent().addClass("active")

});

$(".feature-screenshot").each(function() {
        featureLink = $("<a>").attr({"href": $(this).attr("src"),"data-lightbox":"features","data-title":$(this).next().text()});
        featureLink.insertBefore($(this));
        $(this).appendTo(featureLink);
});

$(function() {
	$(".preloaded").attr("style", "").removeClass("preloaded");
	WebFontConfig = {
		google: { families: [ 'Open+Sans::latin' ] }
	  };
	  (function() {
		var wf = document.createElement('script');
		wf.src = ('https:' == document.location.protocol ? 'https' : 'http') +
		  '://ajax.googleapis.com/ajax/libs/webfont/1/webfont.js';
		wf.type = 'text/javascript';
		wf.async = 'true';
		var s = document.getElementsByTagName('script')[0];
		s.parentNode.insertBefore(wf, s);
	  })(); 
});
