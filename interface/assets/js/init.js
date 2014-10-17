doc = undefined;
elementHeight = undefined;
bodyHeight = undefined;

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

			$(".annotation-wrapper").animate({scrollTop: annotationPage.position().top - paddingTop}, 500);

		}

	});

    /* TESTING */
    setTimeout(function() {
        var d = 0;
        $(".document").each(function() {
            paragraphs = $(this).find("p")

            $(".annotation-page").eq(d).find(".annotation").each(function() {

                var random = Math.floor(Math.random()*paragraphs.length)
                paragraphs.eq(random).addClass("marked").data("for", "annotation-" + $(this).index() )

            });
            d++;
        });

    }, 2000);

    s = Snap("#annotation-connector");
    /* Annotation connector behaviour */
    $("body").on("click", ".marked", function() {

        var documentIndex = $(this).parents(".document").index(".document"),
            markedIndex = $(this).index(".marked"),
            connector = $("#annotation-connector"),
            annotation = $(".annotation-page").eq(documentIndex).find(".annotation").eq(markedIndex)
            thisOffset = $(this).offset(),
            annoOffset = annotation.offset(),
            connOffset = connector.offset();

        left = thisOffset.left + $(this).width();

        // Determine the topmost point.
        t = thisOffset.top<annoOffset.top?thisOffset.top:annoOffset.top;

        // Determine the bottom-most point.
        thisBottom = thisOffset.top + $(this).outerHeight()
        annoBottom = annoOffset.top + annotation.outerHeight()

        b = thisBottom>annoBottom?thisBottom:annoBottom;
        width = annoOffset.left - left;
        connector.css({"top": t, "left": left, "height": b-t, "width" : width});

        var connAnnoTop = annoOffset.top - t,
            connAnnoBottom = connAnnoTop + annotation.outerHeight(),
            connThisTop = thisOffset.top - t,
            connThisBottom = connThisTop + $(this).outerHeight(),
            points = [[width,connAnnoTop], [width,connAnnoBottom], [0,connThisTop], [0,connThisBottom]];

        for(p in points) {
            marker = s.circle(points[p][0], points[p][1], 5);
            marker.attr({
                "fill":"red"

            })
        }
    });

});