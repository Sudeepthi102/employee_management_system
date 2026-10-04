const menuToggle =
    document.getElementById("menuToggle");

const mainNav =
    document.getElementById("mainNav");


if (menuToggle && mainNav) {

    menuToggle.addEventListener(
        "click",
        function () {

            mainNav.classList.toggle("open");

        }
    );
}


function confirmDelete(name) {

    return confirm(
        "Are you sure you want to delete " +
        name +
        "?"
    );

}


document
    .querySelectorAll(".flash")
    .forEach(function (flash) {

        setTimeout(function () {

            flash.style.opacity = "0";

            flash.style.transform =
                "translateY(-10px)";

            setTimeout(function () {

                flash.remove();

            }, 300);

        }, 4500);

    });