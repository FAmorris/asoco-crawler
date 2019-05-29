/*
 *	www.templatemo.com
 *******************************************************/

/* HTML document is loaded. DOM is ready. 
-----------------------------------------*/
$(document).ready(function () {

    /* Mobile menu */
    $('.mobile-menu-icon').click(function () {
        $('.templatemo-left-nav').slideToggle();
    });

    /* Close the widget when clicked on close button */
    $('.templatemo-content-widget .fa-times').click(function () {
        $(this).parent().slideUp(function () {
            $(this).hide();
        });
    });
    $("#sidebar-collapse-button").click(function () {

        if ($(".templatemo-sidebar").hasClass("side-collapse")) {
            $(".templatemo-sidebar").animate({
                width: "280px"
            })
            $.cookie("side-collapse", "no")
        } else {
            $(".templatemo-sidebar").animate({
                width: "5%"
            })
            $.cookie("side-collapse", "yes")
        }
        $(".templatemo-sidebar").toggleClass("side-collapse")
    })
    var sideCollapse = $.cookie("side-collapse")
    if (sideCollapse == "yes") {
        $(".templatemo-sidebar").addClass("side-collapse")
    }
});