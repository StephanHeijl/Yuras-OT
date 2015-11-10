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

$(function() {
	$(".preloaded").attr("style", "").removeClass("preloaded");
});
