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
