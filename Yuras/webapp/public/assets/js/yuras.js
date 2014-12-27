$(function () {
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
	
	console.log($(".delete-document, a[href$='/delete']"))

	$(".delete-document, a[href$='/delete']").click(function (e) {
		e.preventDefault();
		csrfToken = encodeURIComponent($(this).data("csrf"));
		documentId = $(this).data("document-id");
		url = "/documents/" + documentId + "/delete"

		$.post(url, {
			"_csrf_token": csrfToken
		}, function (response) {
			response = JSON.parse(response);
			console.log($("*[data-csrf]"))
			$("*[data-csrf]").each(function() {
				console.log(response.new_csrf)
				console.log($(this).data("csrf"))
				$(this).data("csrf", response.new_csrf);
				console.log($(this).data("csrf"))
				console.log("")
			});
		})
	});
})