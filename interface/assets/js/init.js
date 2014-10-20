doc = undefined;
elementHeight = undefined;
bodyHeight = undefined;
selectedAnnotation = undefined;

currentPage = 0;

$(function() {

    $("link[rel=stylesheet-sass]").each(function() {

        var documentUrl = $(this).attr("href");
        $.get(documentUrl, function(scss) {
            css = Sass.compile(scss);
            $("body").append("<style>"+css+"</style>");
        });

    });

    $(".markdown").each(function() {
        md = $(this).text();
        $(this).html( markdown.toHTML(md) );
    });
});

$(function() {

	/* Divide content over pages. */

	addToPages = function(elements) {
		elements.each(function() {
			bodyHeight = parseInt(doc.find(".document-body").css("height"));
			elementHeight = parseInt($(this).outerHeight(true));

			if(bodyHeight + elementHeight >= doc.innerHeight() - parseInt(doc.find(".document-content-padding").css("padding-top"))*2) {

				children = $(this).children();
				if(children.length > 1) {
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

	setTimeout( function() {
		doc = $(".document").eq(0).clone();
		doc.find(".document-body").html("");
		doc.appendTo($(".document-wrapper"));
		addToPages( $(".document-body").first().children() );
		$(".document").eq(0).remove();
	}, 1000)

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
        t = thisOffset.top<annoOffset.top?thisOffset.top:annoOffset.top;

        // Determine the bottom-most point.
        thisBottom = thisOffset.top + annotatedElement.outerHeight()
        annoBottom = annoOffset.top + annotation.outerHeight()

        b = thisBottom>annoBottom?thisBottom:annoBottom;
        width = annoOffset.left - left;
        connector.css({"top": t, "left": left, "height": b-t, "width" : width});

        var connAnnoTop = annoOffset.top - t,
            connAnnoBottom = connAnnoTop + annotation.outerHeight(),
            connThisTop = thisOffset.top - t,
            connThisBottom = connThisTop + annotatedElement.outerHeight(),
            points = [[width,connAnnoTop], [width,connAnnoBottom], [0,connThisBottom], [0,connThisTop]];

        return points;
    }

    function moveAnnotationConnector(annotatedElement) {
        var points = calculateConnectorPoints(annotatedElement);
        if($("#annotation-connector").children("polyline").length == 0) {
            connection = s.polyline(points);
            connection.attr({
                "id":"annotation-connection"
            });

            bg = annotatedElement.css("background-color");

            c = Snap.color(bg);
            gradBg = "rgba(" + [c["r"]-40,c["g"]-40,c["b"]-40,c["opacity"]].join(",") +")" + "-rgb(" + [c["r"]-40,c["g"]-40,c["b"]-40].join(",") + ")";
            console.log(gradBg)

            g = s.gradient("l(0,0,1,0)"+gradBg);

            connection.attr({
                //"fill":annotatedElement.css("background-color"),
                "fill":g,
                "points":points.join(",")
            })
        } else {
            connection = Snap.select("#annotation-connection")

            oldPoints = connection.attr("points");
            betweenPoints = oldPoints.slice(0,5).join(",") + points.slice(2,5).join(",");

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
                "points":points.join(",")
            })
        }
    }

    s = Snap("#annotation-connector");

    $("body").on("click", ".marked", function() {
        moveAnnotationConnector($(this));
        selectedAnnotation = $(this);
    });


	/* Handle switching the annotation page */
	$(window).on("scroll", function() {
		var st = $("body").scrollTop();
		tmpCurrentPage = -1;
		$(".document").each(function() {
			var distance = st - $(this).offset().top;
			if( distance > 0 ) {
				tmpCurrentPage++;
			}
		});

		tmpCurrentPage = (tmpCurrentPage<0)?0:tmpCurrentPage;

		if( tmpCurrentPage != currentPage) {
			currentPage = tmpCurrentPage;
			console.log("Switched page")
			var annotationPages = $(".annotation-page");

			if( annotationPages.length <= currentPage) {
				return false;
			}

			console.log( " Annotations available. ")
			var annotationPage = $(".annotation-page").eq(currentPage);
			var paddingTop = parseInt($(".annotation-wrapper-padding").css("padding-top"));

			$(".annotation-wrapper").animate({scrollTop: annotationPage.position().top - paddingTop}, 
				{"duration":500, 
				 "step": function() {
						/* Scrolling the annotation marker, called on each step of the animation to provide a smooth transition*/
						if(typeof selectedAnnotation !== "undefined") {
				            		moveAnnotationConnector(selectedAnnotation);
						}
					}
				}
			);

		}

		/* Scrolling the annotation marker */
		if(typeof selectedAnnotation !== "undefined") {
            		moveAnnotationConnector(selectedAnnotation);
		}


	});

    /* TESTING - This adds annotated elements to each page randomly.*/
    setTimeout(function() {
        var d = 0;
        $(".document").each(function() {
            paragraphs = $(this).find("p")

            $(".annotation-page").eq(d).find(".annotation").each(function() {

                var random = Math.floor(Math.random()*paragraphs.length);
                paragraphs.eq(random).addClass("marked").data("for", "annotation-" + $(this).parent().index(this) );

            });
            d++;
        });

    }, 1000);

});
