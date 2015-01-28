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


		// Adds a confirm dialog to elements that may be deleted
		$("a[href$='/delete']").click(function (e) {
			e.preventDefault()
			confirmDelete = window.confirm("Are you sure you want to remove this?")
			if (!confirmDelete) {
				e.stopImmediatePropagation() // This stops all other events from executing
			} else {
				$(this).parents("tr").fadeOut() // This fades out the parent table row.
			}
		});

		// Handle links with csrf requirements
		$("a[data-csrf]").click(function (e) {
			e.preventDefault();
			csrfToken = encodeURIComponent($(this).data("csrf"));
			url = $(this).attr("href")
			$.post(url, {
				"_csrf_token": csrfToken
			}, function (response, textStatus) {
				if (textStatus != "success") {
					return false; // Handle csrf errors here
				}
				response = JSON.parse(response);
				$("a[data-csrf]").each(function () {
					$(this).data("csrf", response.new_csrf);
				});
			})
		});

		// Handle page and amount info from hash
		function setPageInfo(page, amount) {
			window.location.hash = "#" + page + "," + amount
		}

		function getPageInfo() {
			pageHash = window.location.hash
			pageInfo = pageHash.slice(1).split(",")
			if (pageInfo.length < 2) {
				return [0, 10]
			}
			return [parseInt(pageInfo[0]), parseInt(pageInfo[1])]
		}

		// Handle pagination
		function changePage(difference) {
			pageInfo = getPageInfo()
			page = pageInfo[0]
			amount = pageInfo[1]
			url = window.location.href.split("#")[0] + "table/" + amount + "/" + (page + difference)

			$("table tbody").load(url)
			setPageInfo(page + difference, amount);
			$(".prev-page").attr("disabled", page+difference <= 0)
		}

		$(".next-page").click(function (e) {
			changePage(1)
		})

		$(".prev-page").click(function (e) {
			changePage(-1)
		})

		// Set to the proper page if there are prev/next buttons
		if($(".next-page, .prev-page").length >= 2) {
			changePage(0);	
		}
	
});