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
