doc = undefined;
elementHeight = undefined;
bodyHeight = undefined;
selectedAnnotation = undefined;

currentPage = 0;

$(function () {

	$("link[rel=stylesheet-sass]").each(function () {

		var documentUrl = $(this).attr("href");
		$.get(documentUrl, function (scss) {
			css = Sass.compile(scss);
			$("body").append("<style>" + css + "</style>");
		});

	});

	$(".markdown").each(function () {
		md = $(this).text();
		//$(this).html( markdown.toHTML(md) );

	});
});

$(function () {

	/* Divide content over pages. */

	addToPages = function (elements) {
		elements.each(function () {
			bodyHeight = parseInt(doc.find(".document-body").css("height"));
			elementHeight = parseInt($(this).outerHeight(true));

			if (bodyHeight + elementHeight >= doc.innerHeight() - parseInt(doc.find(".document-content-padding").css("padding-top")) * 2) {

				children = $(this).children();
				if (children.length > 1) {
					addToPages(children);
					return;
				}

				doc.appendTo($(".wrapper"));
				doc = $(".document").eq(0).clone();
				doc.find(".document-body").html("");
				doc.appendTo($(".document-wrapper"));

			}
			$(this).appendTo(doc.find(".document-body"));
		});
	}

	function reflowPages() {
		doc = $(".document").eq(0).clone();
		doc.find(".document-body").html("");
		doc.appendTo($(".document-wrapper"));
		addToPages($(".document-body").first().children());
		$(".document").eq(0).remove();
	}

	//reflowPages()

	/* Annotation connector behaviour */
	function calculateConnectorPoints(annotatedElement) {
		var documentIndex = annotatedElement.parents(".document").index(".document"),
			markedLinkedTo = annotatedElement.data("linked-to"),
			connector = $("#annotation-connector"),
			annotation = $(".annotation-page").eq(documentIndex).find(".annotation[data-linked-to=" + markedLinkedTo + "]")
		thisOffset = annotatedElement.offset(),
			annoOffset = annotation.offset(),
			connOffset = connector.offset();

		left = thisOffset.left + annotatedElement.width();
		left += 2.5; /* Compensate for padding */

		// Determine the topmost point.
		t = thisOffset.top < annoOffset.top ? thisOffset.top : annoOffset.top;

		// Determine the bottom-most point.
		thisBottom = thisOffset.top + annotatedElement.outerHeight()
		annoBottom = annoOffset.top + annotation.outerHeight()

		b = thisBottom > annoBottom ? thisBottom : annoBottom;
		width = annoOffset.left - left;
		connector.css({
			"top": t,
			"left": left,
			"height": b - t,
			"width": width
		});

		var connAnnoTop = annoOffset.top - t,
			connAnnoBottom = connAnnoTop + annotation.outerHeight(),
			connThisTop = thisOffset.top - t,
			connThisBottom = connThisTop + annotatedElement.outerHeight(),
			points = [[width, connAnnoTop], [width, connAnnoBottom], [0, connThisBottom], [0, connThisTop]];

		return points;
	}

	function moveAnnotationConnector(annotatedElement) {
		var points = calculateConnectorPoints(annotatedElement);
		if ($("#annotation-connector").children("polyline").length == 0) {
			connection = s.polyline(points);
			connection.attr({
				"id": "annotation-connection"
			});

			bg = annotatedElement.css("background-color");

			c = Snap.color(bg);
			gradBg = "rgba(" + [c["r"], c["g"], c["b"], c["opacity"]].join(",") + ")" + "-rgb(" + [c["r"], c["g"], c["b"]].join(",") + ")";

			g = s.gradient("l(0,0,1,0)" + gradBg);

			connection.attr({
				//"fill":annotatedElement.css("background-color"),
				"stroke": g,
				"stroke-width": 2,
				"fill": "transparent",
				"points": points.join(",")
			})
		} else {
			connection = Snap.select("#annotation-connection")

			oldPoints = connection.attr("points");
			betweenPoints = oldPoints.slice(0, 5).join(",") + points.slice(2, 5).join(",");

			/* Animated */
			/*
            connection.attr({
                "points":betweenPoints
            });

            connection.animate({
                "points":points.join(",")
            },200)
            */
			/* Non-animated */
			connection.attr({
				"points": points.join(",")
			})
		}
	}

	scrollToSelectedAnnotation = function (annotatedElement) {
		var markedLinkedTo = annotatedElement.data("linked-to"),
			annotation = $(".annotation[data-linked-to=" + markedLinkedTo + "]"),
			paddingTop = parseInt($(".annotation-wrapper-padding").css("padding-top"));
		$(".annotation-wrapper").animate({
			scrollTop: annotation.position().top - paddingTop
		}, {
			"duration": 500,
			"step": function () {
				/* Scrolling the annotation marker, called on each step of the animation to provide a smooth transition*/
				if (typeof selectedAnnotation !== "undefined") {
					moveAnnotationConnector(selectedAnnotation);
				}
			}
		});
	}

	s = Snap("#annotation-connector");

	$("body").on("click", ".marked", function () {
		if($(this).hasClass("article")) {
			return;	
		}
		moveAnnotationConnector($(this));
		scrollToSelectedAnnotation($(this))
		selectedAnnotation = $(this);
	});


	/* Handle switching the annotation page */
	$(window).on("scroll", function () {
		var st = $("body").scrollTop();
		tmpCurrentPage = -1;
		$(".document").each(function () {
			var distance = st - $(this).offset().top + parseInt($(".annotation-wrapper").css("top"));
			if (distance > 0) {
				tmpCurrentPage++;
			}
		});

		tmpCurrentPage = (tmpCurrentPage < 0) ? 0 : tmpCurrentPage;

		if (tmpCurrentPage != currentPage) {
			currentPage = tmpCurrentPage;
			console.log("Switched page")
			var annotationPages = $(".annotation-page");

			if (annotationPages.length <= currentPage) {
				return false;
			}

			console.log(" Annotations available. ")
			var annotationPage = $(".annotation-page").eq(currentPage);
			var paddingTop = parseInt($(".annotation-wrapper-padding").css("padding-top"));

			$(".annotation-wrapper").animate({
				scrollTop: annotationPage.position().top - paddingTop
			}, {
				"duration": 500,
				"step": function () {
					/* Scrolling the annotation marker, called on each step of the animation to provide a smooth transition*/
					if (typeof selectedAnnotation !== "undefined") {
						moveAnnotationConnector(selectedAnnotation);
					}
				}
			});

		}

		/* Scrolling the annotation marker */
		if (typeof selectedAnnotation !== "undefined") {
			moveAnnotationConnector(selectedAnnotation);
		}

	});

	function saveDocument() {
		csrfToken = encodeURIComponent($("#csrf-token").data("csrf"))
		html = ""
		$(".document-body").each(function () {
			html += $(this).html()
		});
		contents = encodeURIComponent(html);
		title = encodeURIComponent($("#document-title").text());
		url = window.location.href.replace("#", "") + "/save"
		category = $("#category").text()

		annotations = {};

		$(".annotation").each(function () {
			annotations[$(this).data("annotation-id")] = {
				"text": $(this).html().trim(),
				"location": $(this).data("location"),
				"selected_text": $(this).data("selected_text"),
				"linked-to": $(this).data("linked-to")
			};
		});

		console.log(annotations)

		annotations = encodeURIComponent(JSON.stringify(annotations));

		$.post(url, {
			"contents": contents,
			"annotations": annotations,
			"category": category,
			"title": title,
			"_csrf_token": csrfToken
		}, function (response) {
			response = JSON.parse(response);
			$("#csrf-token").data("csrf", response.new_csrf);
			$("#document-title").removeClass("not-saved");
		})
	}

	$(window).bind('keydown', function (event) {
		if (event.ctrlKey || event.metaKey) {
			switch (String.fromCharCode(event.which).toLowerCase()) {
			case 's':
				event.preventDefault();
				saveDocument()
				break;
			}
		}
	});

	function zoomInAnnotation(annotation, delay) {
		setTimeout(function () {
			annotation.css({
				"transform": "scale(1)"
			})
			$(".marked[data-linked-to=" + annotation.data("linked-to") + "]").css({
				"transform": "scale(1)"
			})
		}, delay);
	}

	function addAnnotation(start, length, text, annotationContents, page) {
		annotation = $("<div>");
		annotation.addClass("annotation");
		if (typeof page === "undefined") {
			page = 0;
		}
		if (typeof annotationContents === "undefined") {
			annotation.attr("contenteditable", "true");
			annotation.html("Add annotation text here");
		} else {
			annotation.html(annotationContents);
		}

		pages = $(".annotation-page").length
		while (pages <= page) {
			$(".annotation-wrapper-padding").append("<div class='annotation-page'></div>")
			pages = $(".annotation-page").length
		}

		annotation.appendTo($(".annotation-page").eq(page))
		annotation.css({
			"transform": "scale(0)"
		})
		zoomInAnnotation(annotation, $(".annotation").length * 10)

		annotation.data("annotation-id", "undefined-" + $(".annotation").length)
		annotation.data("location", start + "," + length)
		annotation.data("selected_text", text)
		annotation.attr("data-linked-to", $(".annotation-page .annotation").length)
		annotation.click(function () {
			if ($(this).attr("contenteditable")) {
				$(this).html("");
				$(this).unbind("click");
			}
		})
		console.log("Scaled to 1")

	}

	$("#annotate-selection").click(function (e) {
		e.preventDefault()

		var sel = window.getSelection();

		if (sel.getRangeAt && sel.rangeCount) {
			range = sel.getRangeAt(0);
			text = sel.anchorNode.data.substr(range.startOffset, (range.endOffset - range.startOffset))

			range.deleteContents();
			markerContainer = document.createElement("span");
			markerContainer.className = "marked";
			markerContainer.appendChild(document.createTextNode(text))
			range.insertNode(markerContainer);
		}

		addAnnotation(range.startOffset, text.length, text);
	});

	$("#annotate-word").click(function (e) {
		e.preventDefault()
		var sel = window.getSelection(),
			wordStart = sel.baseOffset,
			wordEnd = sel.baseOffset,
			text = sel.anchorNode.data;

		while (text.charAt(wordStart) !== " " && wordStart > 0) {
			wordStart--;
		}
		while (text.charAt(wordEnd) !== " " && wordEnd < text.length) {
			wordEnd++;
		}

		text = text.substr(wordStart + 1, (wordEnd - wordStart - 1))
		console.log(wordStart, wordEnd, text);

		if (sel.getRangeAt && sel.rangeCount) {
			range = sel.getRangeAt(0);
			range.setStart(sel.anchorNode, wordStart + 1)
			range.setEnd(sel.anchorNode, wordEnd)
			range.deleteContents();
			markerContainer = document.createElement("span");
			markerContainer.className = "marked";
			markerContainer.setAttribute("data-annotation", $(".annotation").length - 1);
			markerContainer.appendChild(document.createTextNode(text))
			range.insertNode(markerContainer);
		}

		addAnnotation(range.startOffset, text.length, text);

	});

	$("#annotate-sentence").click(function (e) {
		e.preventDefault()
		var sel = window.getSelection(),
			sentenceStart = sel.baseOffset,
			sentenceEnd = sel.baseOffset,
			text = sel.anchorNode.data;

		while (text.charAt(sentenceStart) !== "." && sentenceStart > 0) {
			sentenceStart--;
		}
		while (text.charAt(sentenceEnd) !== "." && sentenceEnd < text.length) {
			sentenceEnd++;
		}

		text = text.substr(sentenceStart, (sentenceEnd - sentenceStart + 1))

		if (sel.getRangeAt && sel.rangeCount) {
			range = sel.getRangeAt(0);
			range.setStart(sel.anchorNode, sentenceStart)
			range.setEnd(sel.anchorNode, sentenceEnd + 1)
			range.deleteContents();
			markerContainer = document.createElement("span");
			markerContainer.className = "marked";
			markerContainer.appendChild(document.createTextNode(text))
			range.insertNode(markerContainer);
		}

		addAnnotation(range.startOffset, text.length, text);

	});

	$("#annotate-paragraph").click(function (e) {
		e.preventDefault()
		var sel = window.getSelection();
		console.log(sel)
		sel.baseNode.parentElement.className += " marked"
		sel.baseNode.parentElement.style.display = "block"
	});

	$("#document-title").click(function () {

		currentTitle = $(this).text()
		titleInput = $("<input>")
		titleInput.attr("id", "document-title-input")
		titleInput.attr("value", currentTitle)
		$(this).html("");
		titleInput.click(function () {
			return false;
		})
		titleInput.appendTo($(this))
		titleInput.blur(function () {
			newTitle = $(this).val()
			if (newTitle.length > 0) {
				$(this).parent().text(newTitle);
			} else {
				$(this).parent().text(currentTitle);
			}
		})
		titleInput.focus()

	});

	$("#create-new-category").click(function (e) {
		e.preventDefault();

		currentCategory = $("#category").text()
		$(".category-dropdown").hide(0)
		categoryInput = $("<input>").addClass("form-control input-lg");
		categoryInput.appendTo($(".category-container"))
		categoryInput.focus()

		categoryInput.blur(function () {
			$(".category-dropdown").show(0)
			$("#category").text($(this).val())
			$(this).hide(0, function () {
				$(this).remove();
			});
		})

	});

	$(".category-menu-option").click(function (e) {
		e.preventDefault()
		$("#category").text($(this).text())
	});

	$("body").on("change input", ".document-body", function (e) {
		e.stopPropagation()
		$("#document-title").addClass("not-saved");
	})

	$("#save-document").click(function (e) {
		e.preventDefault()
		saveDocument()
	});


	// Handle getting related documents	
	$("#get-related").click(function (e) {
		modalBody = $("#relatedModal .modal-body")
		documentIcon = modalBody.find(".case-document")

		if (documentIcon.length == 1) {
			$.getJSON(window.location.href.replace("#", "") + "/related", function (data) {
				modalBody.find(".related-loader").remove()

				$.each(data, function (d, doc) {
					icon = documentIcon.clone()
					icon.find(".case-document-title").text(doc[1]).attr("href", "/documents/" + doc[0])
					icon.data("score", doc[2])
					icon.attr("data-id", doc[0])
					$(".modal-body .row").last().append(icon)
					if ($(".modal-body .row").last().children().length == 3) {
						$(".modal-body .container-fluid").append("<div class='row'></div>")
					}
					icon.fadeIn()
					console.log(icon)
				})

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
			});
		}


	});
	
	// Handle picking a case
	$(".case-menu-option").click( function(e) {
		console.log($(this).data("case-id"))
		$("#chosen-case").text($(this).text()).data("case-id", $(this).data("case-id"))
	});

	// Handle document analysis
	$("#analyze-document").click(function (e) {
		e.preventDefault()

		$(this).unbind("click").parent().addClass("disabled") // Disable button after it has been clicked.

		// Add overlay
		overlay = $("<div>")
		overlay.addClass("document-overlay");
		overlay.css({
			"display": "none"
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


		$.getJSON(window.location.href.replace("#", "") + "/tfidf", function (data) {
			console.log(data);

			loader.css({
				"transform": "scale(0)"
			})

			setTimeout(function () {
				overlay.fadeOut(300);
			}, 500)

			$.each(data, function (word, related) {
				regex = RegExp(word, "i")

				contents = ""
				$.each(related, function (i, r) {
					console.log(r)
					contents += "<a target='_blank' href='/documents/" + r._id + "'>" + r.title + "</a><br/>"
				});

				if (contents == "") {
					contents = "No related articles found."
				}

				$(".document-body").each(function (page) {
					start = $(this).text().search(regex)
					if (start >= 0) {
						console.log("Adding annotation for word " + word + " to page " + page)
						addAnnotation(start, word.length, word, contents, page)
						$(this).html(
							$(this).html().replace(regex, "<span class='marked' data-linked-to='" + $(".annotation").length + "' style='transform: scale(0)'>" + word + "</span>")
						)
						return true
					} else {
						return false
					}
				});
			})

			// Sort the annotations on each page
			$(".annotation-page").each(function () {
				annotations = $(this).children(".annotation")
				annotations.sort(function (a, b) {
					al = parseInt($(a).data("location").split(",")[0])
					bl = parseInt($(b).data("location").split(",")[0])
					if (al > bl) {
						return 1
					} else if (al < bl) {
						return -1
					}
					return 0
				})
				annotations.detach().appendTo($(this));

			})
		});
	});

});