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
		overlay.css({"display":"none","background":"transparent"})
		loader = $("<div>").addClass("document-loader")
		loader.appendTo(overlay)
		overlay.appendTo( $("body") )
		
		loader.css({"transform":"scale(0)"})
		overlay.fadeIn(300, function() {
			loader.css({"transform":"scale(1)"})
		})
		
		$("table tbody").load(url, function() {
			// Reset overlay
			loader.css({"transform":"scale(0)"})
			
			setTimeout(function() {
				overlay.remove();
			},500)
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
		if(getPageInfo()[0]>9) {
			changePage(0);	
		}
	}

	// Handle category selection
	$('.category-option').click(function() {
		$('.category-dropdown-text').text($(this).text());
		$('.category-input').val($(this).data('value'));
	});
	
	// Handle heatcolor of related rating when they are present on load
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
			url: "/cases/"+$("#chosen-case").data("case-id")+"/add", 
			data :{
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
			url: "/cases/"+$("#chosen-case").data("case-id")+"/remove", 
			data :{
				"document_id": caseDocument.data("id"),
				"_csrf_token": csrfToken
			},
			success: function (response) {
				console.log(response)
				$("#csrf-token").data("csrf", response.new_csrf);
				caseDocument.fadeOut( 500, caseDocument.remove )
			},
			dataType: "json"
		});

	});
});