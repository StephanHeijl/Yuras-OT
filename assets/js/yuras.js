var GhostUserAgent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.121 Safari/535.2";

if( navigator.userAgent !== GhostUserAgent ) {

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
			featureLink = $("<a>").attr({"href": $(this).attr("src").replace("screenshots_thumbs", "screenshots"),"data-lightbox":"features","data-title":$(this).next().text()});
			featureLink.insertBefore($(this));
			$(this).appendTo(featureLink);
	});

	$(".preloaded").attr("style", "").removeClass("preloaded");

	(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
	  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
	  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
	  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

	  ga('create', 'UA-61117358-2', 'auto');
	  ga('send', 'pageview');
	
} else {
	$(function() {
		$("div[id^=lightbox]").remove();
	});
}