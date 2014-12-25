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
		//$(".document").eq(0).remove();
	}

	reflowPages()

	/* Annotation connector behaviour */
	function calculateConnectorPoints(annotatedElement) {
		var documentIndex = annotatedElement.parents(".document").index(".document"),
			markedIndex = annotatedElement.index(".marked"),
			connector = $("#annotation-connector"),
			annotation = $(".annotation-page").eq(documentIndex).find(".annotation").eq(markedIndex)
		thisOffset = annotatedElement.offset(),
		annoOffset = annotation.offset(),
		connOffset = connector.offset();

		left = thisOffset.left + annotatedElement.width();
		left += 10; /* Compensate for padding */

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
				"fill": g,
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

	s = Snap("#annotation-connector");

	$("body").on("click", ".marked", function () {
		moveAnnotationConnector($(this));
		selectedAnnotation = $(this);
	});


	/* Handle switching the annotation page */
	$(window).on("scroll", function () {
		var st = $("body").scrollTop();
		tmpCurrentPage = -1;
		$(".document").each(function () {
			var distance = st - $(this).offset().top;
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
		csrfToken = encodeURIComponent($("#save-document").data("csrf"))
		html = ""
		$(".document-body").each(function () {
			html += $(this).html()
		});
		contents = encodeURIComponent(html);
		title = encodeURIComponent($("#document-title").text());
		url = window.location.href.replace("#", "") + "/save"
		annotations = {};
		
		$(".annotation").each(function() {
			annotations[$(this).data("annotation-id")] = $(this).html().trim();
		});
		
		console.log(annotations)
		console.log(JSON.stringify(annotations))
		annotations = encodeURIComponent( JSON.stringify(annotations) );
		console.log(annotations)
		

		$.post(url, {
			"contents": contents,
			"annotations": annotations,
			"title": title,
			"_csrf_token": csrfToken
		}, function (response) {
			response = JSON.parse(response);
			$("#save-document").data("csrf", response.new_csrf);
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
	
	function addAnnotation() {
		annotation = $("<div>");
		annotation.addClass("annotation");
		annotation.attr("contenteditable","true")
		annotation.appendTo(".annotation-page");
		annotation.html("<em>Add annotation text here</em>")
		annotation.click(function() { $(this).html(""); $(this).unbind("click") })
	}
	
	$("#annotate-selection").click(function(e) {
		e.preventDefault()
		var sel = window.getSelection(),
			text = sel.anchorNode.data.substr(sel.baseOffsset, (sel.extentOffset-sel.baseOffset))
		if (sel.getRangeAt && sel.rangeCount) {
            range = sel.getRangeAt(0);
			console.log(range)
            range.deleteContents();
			markerContainer = document.createElement("span");
			markerContainer.className = "marked";
			markerContainer.appendChild( document.createTextNode(text) )
            range.insertNode( markerContainer );
        }
		
		addAnnotation();
	});
	
	$("#annotate-word").click(function(e) {
		e.preventDefault()
		var sel = window.getSelection(),
			wordStart = sel.baseOffset,
			wordEnd = sel.baseOffset,
			text = sel.anchorNode.data;
		
		while ( text.charAt(wordStart) !== " " && wordStart > 0) {
			wordStart--;
		}
		while ( text.charAt(wordEnd) !== " " && wordEnd < text.length) {
			wordEnd++;
		}
		
		text = text.substr(wordStart+1,(wordEnd-wordStart-1))
		console.log(wordStart, wordEnd, text);
		
		if (sel.getRangeAt && sel.rangeCount) {
            range = sel.getRangeAt(0);
			range.setStart(sel.anchorNode,wordStart)
			range.setEnd(sel.anchorNode,wordEnd)
            range.deleteContents();
			markerContainer = document.createElement("span");
			markerContainer.className = "marked";
			markerContainer.setAttribute("data-annotation",$(".annotation").length);
			markerContainer.appendChild( document.createTextNode(text) )
            range.insertNode( markerContainer );
        }
		
		addAnnotation();
		
	});
	
	$("#annotate-sentence").click(function(e) {
		e.preventDefault()
		var sel = window.getSelection(),
			sentenceStart = sel.baseOffset,
			sentenceEnd = sel.baseOffset,
			text = sel.anchorNode.data;
		
		while ( text.charAt(sentenceStart) !== "." && sentenceStart > 0) {
			sentenceStart--;
		}
		while ( text.charAt(sentenceEnd) !== "." && sentenceEnd < text.length) {
			sentenceEnd++;
		}
		
		text = text.substr(sentenceStart+1,(sentenceEnd-sentenceStart-1))
		console.log(sentenceStart, sentenceEnd, text);
		
		if (sel.getRangeAt && sel.rangeCount) {
            range = sel.getRangeAt(0);
			range.setStart(sel.anchorNode,sentenceStart)
			range.setEnd(sel.anchorNode,sentenceEnd)
            range.deleteContents();
			markerContainer = document.createElement("span");
			markerContainer.className = "marked";
			markerContainer.appendChild( document.createTextNode(text) )
            range.insertNode( markerContainer );
        }
		
		addAnnotation();
		
	});
	
	$("#document-title").click(function() {
		
		currentTitle = $(this).text()
		titleInput = $("<input>")
		titleInput.attr("id","document-title-input")
		titleInput.attr("value",currentTitle)
		$(this).html("");
		titleInput.click(function() { return false; })
		titleInput.appendTo($(this))
		titleInput.blur(function() {
			newTitle = $(this).val()
			if (newTitle.length > 0) {
				$(this).parent().text(newTitle);	
			} else {
				$(this).parent().text(currentTitle);
			}
		})
		titleInput.focus()
		
	});
	
	$("body").on("change input",".document-body", function(e) {
		e.stopPropagation()
		$("#document-title").addClass("not-saved");
	})
	
	$("#annotate-paragraph").click(function(e) {
		e.preventDefault()
		var sel = window.getSelection();
		console.log(sel)
		sel.baseNode.parentElement.className += " marked"
	});

	$("#save-document").click(function (e) {
		e.preventDefault()
		saveDocument()
	});

});