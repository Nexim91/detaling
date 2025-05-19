console.log("price_uslugi_carousel.js loaded");

document.addEventListener('DOMContentLoaded', function () {
    // Инициализация карусели для каждого таба с товарами
    const carousels = document.querySelectorAll('.owl-carousel');
    carousels.forEach(carousel => {
        $(carousel).owlCarousel({
            loop: false,
            margin: 10,
            nav: true,
            dots: true,
            responsive: {
                0: {
                    items: 1
                },
                576: {
                    items: 2
                },
                768: {
                    items: 3
                },
                992: {
                    items: 4
                }
            }
        });
    });

    // Обработка переключения табов для обновления карусели
    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        const target = $(e.target).attr('href');
        $(target).find('.owl-carousel').trigger('refresh.owl.carousel');
    });
});
