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
		baseUrl = window.location.href.split("#")[0]
		getParameters = baseUrl.split("?")[1]

		basePath = baseUrl.split("?")[0]
		if (basePath.substr(-1) != "/") {
			basePath += "/"
		}
		url = basePath + "table/" + amount + "/" + (page + difference) + "?" + getParameters

		// Add overlay and loader
		overlay = $("<div>")
		overlay.addClass("document-overlay");
		overlay.css({
			"display": "none",
			"background": "transparent"
		})
		loader = $("<div>").addClass("document-loader")
		loader.appendTo(overlay)
		overlay.appendTo($("body"))

		loader.css({
			"transform": "scale(0)"
		})
		overlay.fadeIn(300, function () {
			loader.css({
				"transform": "scale(1)"
			})
		})

		$("table tbody").load(url, function () {
			// Reset overlay
			loader.css({
				"transform": "scale(0)"
			})

			setTimeout(function () {
				overlay.remove();
			})
		})
		setPageInfo(page + difference, amount);
		$(".prev-page").attr("disabled", page + difference <= 0)
	}

	$(".next-page").click(function (e) {
		changePage(1)
	})

	$(".prev-page").click(function (e) {
		changePage(-1)
	})

	// Set to the proper page if there are prev/next buttons
	if ($(".next-page, .prev-page").length >= 2) {
		if (getPageInfo()[0] > 9) {
			changePage(0);
		}
	}

	// Handle category selection
	$('.category-option').click(function () {
		$('.category-dropdown-text').text($(this).text());
		$('.category-input').val($(this).data('value'));
	});

	// Handle heatcolor of related rating when they are present on load
	if ($(".related-document-rating").length > 0) {
		$(".related-document-rating").heatcolor(
			function () {
				$(this).width(12 + (($(this).parent().data("score") - 0.5) * 48))
				return $(this).parent().data("score");
			}, {
				lightness: 0,
				colorStyle: 'greentored',
				maxval: 1,
				minval: 0.5,
			});
	}

	// Handle adding related document to case 	
	$("body").on("click", ".related-document-add", function (e) {
		csrfToken = encodeURIComponent($("#csrf-token").data("csrf"))
		$(this).css({
			"background": "#337ab7",
			"color": "white",
			"border-color": "white"
		});
		$(this).find(".glyphicon").attr("class", "glyphicon glyphicon-ok");

		$.ajax({
			type: "POST",
			url: "/cases/" + $("#chosen-case").data("case-id") + "/add",
			data: {
				"document_id": $(this).parents(".case-document").data("id"),
				"_csrf_token": csrfToken
			},
			success: function (response) {
				console.log(response)
				$("#csrf-token").data("csrf", response.new_csrf);
				$(".add-related-document-warning").fadeIn()
			},
			dataType: "json"
		});
	});

	// Handle removing related document to case 	
	$("body").on("click", ".related-document-remove", function (e) {
		csrfToken = encodeURIComponent($("#csrf-token").data("csrf"))
		caseDocument = $(this).parents(".case-document")
		$.ajax({
			type: "POST",
			url: "/cases/" + $("#chosen-case").data("case-id") + "/remove",
			data: {
				"document_id": caseDocument.data("id"),
				"_csrf_token": csrfToken
			},
			success: function (response) {
				console.log(response)
				$("#csrf-token").data("csrf", response.new_csrf);
				caseDocument.fadeOut(500, caseDocument.remove)
			},
			dataType: "json"
		});
	});

	// Handle changing a case title
	function changeCaseTitle(title) {
		$(".display-title .case-title").text(title)
		$(".case-title-editor").attr("placeholder", title)

		csrfToken = encodeURIComponent($("#csrf-token").data("csrf"))
		$.ajax({
			type: "POST",
			url: "/cases/" + $("#chosen-case").data("case-id") + "/set-title",
			data: {
				"document_title": title,
				"_csrf_token": csrfToken
			},
			success: function (response) {
				$("#csrf-token").data("csrf", response.new_csrf);
			},
			dataType: "json"
		});
	}

	// Handle case title transfering
	$("#edit-case-title").click(function (e) {
		e.preventDefault()
		$(this).parents(".display-title").hide()
		$(".edit-title").show()
		$(".case-title-editor").bind("blur submit", function () {
			changeCaseTitle($(this).val())
			$(".edit-title").hide()
			$(".display-title").show()
		})
	});


	setDocumentItemProperties = function () {
		$(".document-item").each(function () {
			$(this).data("absoluteTop", $(this).offset().top + $(this).height())
			$(this).data("absoluteHeight", $(this).height())
		})
	}
	setDocumentItemProperties()

// Handle document clicking in the search and documents pages
$(".document-item").click(function () {
	highlightContainer = $(".document-highlight-container")
	$(".document-highlight-container").not(highlightContainer).removeClass("visible")
	highlightContainer.find(".document-title").text($(this).find(".document-title").text())
	highlightContainer.addClass("visible")

	pointer = highlightContainer.find(".document-highlight-pointer-container")
	pointer.css({
		"left": $(this).offset().left + ($(this).width() / 2) - 22
	})

	perline = Math.floor(1 / ($(this).outerWidth() / $(this).parent().width()))
	row = Math.floor($(this).index() / perline)
	lastindex = ((row + 1) * perline)

	highlightContainer.css({
		"top": $(this).data("absoluteTop") + (row * 5)
	})

	if (lastindex !== highlightContainer.data("lastindex")) {
		$(".document-item").height("").animate({
			"margin-bottom": "20px"
		})
		h = highlightContainer.outerHeight()
		if (h < 10) {
			h = $(this).height();
		}
		console.log(h)
		$(this).animate({
			"margin-bottom": h + 50
		})
	}

	highlightContainer.data("lastindex", lastindex)
});

});