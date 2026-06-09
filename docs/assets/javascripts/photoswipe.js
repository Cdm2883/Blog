(function () {

const IC_CLOSE = '<svg class="pswp__icn" viewBox="0 0 24 24" aria-hidden="true"><path fill="var(--pswp-icon-color)" d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>';
const IC_ZOOM = '<svg class="pswp__icn" viewBox="-1.333 -1.533 26.667 26.667" aria-hidden="true"><path fill="var(--pswp-icon-color)" d="m15.5 14 5 5-1.5 1.5-5-5v-.79l-.27-.28A6.47 6.47 0 0 1 9.5 16 6.5 6.5 0 0 1 3 9.5 6.5 6.5 0 0 1 9.5 3 6.5 6.5 0 0 1 16 9.5c0 1.61-.59 3.09-1.57 4.23l.28.27zm-6 0C12 14 14 12 14 9.5S12 5 9.5 5 5 7 5 9.5 7 14 9.5 14m2.5-4h-2v2H9v-2H7V9h2V7h1v2h2z"/></svg>';
const IC_ARROW = '<svg class="pswp__icn" viewBox="-159.058 -159.158 795.292 795.292" aria-hidden="true"><path fill="var(--pswp-icon-color)" d="M145.188 238.575 360.688 23.075c5.3-5.3 5.3-13.8 0-19.1s-13.8-5.3-19.1 0l-225.1 225.1c-5.3 5.3-5.3 13.8 0 19.1l225.1 225c2.6 2.6 6.1 4 9.5 4s6.9-1.3 9.5-4c5.3-5.3 5.3-13.8 0-19.1z"/></svg>';

const isVisible = (image, style = getComputedStyle(image)) =>
    style.display !== "none" && style.visibility !== "hidden" && image.getClientRects().length > 0;
const imageSize = (
    image,
    width = Number(image.dataset.pswpWidth) || image.naturalWidth || Math.round(image.getBoundingClientRect().width),
    height = Number(image.dataset.pswpHeight) || image.naturalHeight || Math.round(image.getBoundingClientRect().height)
) => ({
    width: width > 0 ? width : 1200,
    height: height > 0 ? height : 900
});
const createItem = (
    image,
    size = imageSize(image)
) => ({
    src: image.dataset.pswpSrc,
    msrc: image.currentSrc || image.src,
    width: size.width,
    height: size.height,
    alt: image.alt || "",
    element: image
});
const waitForImage = image => image.complete
    ? Promise.resolve()
    : new Promise(resolve => {
        image.addEventListener("load", resolve, { once: true });
        image.addEventListener("error", resolve, { once: true });
    })

function mountPhotoSwipe() {
    if (!window.PhotoSwipe) return;

    const images = Array.from(document.querySelectorAll(".md-content article img[data-pswp-src]"));
    images.forEach(image => {
        if (image.dataset.pswpBound) return;

        image.dataset.pswpBound = "true";
        image.addEventListener("click", async event => {
            event.preventDefault();
            await waitForImage(image);

            const visibleImages = images.filter(it => isVisible(it));
            const items = visibleImages.map(it => createItem(it));
            const index = visibleImages.indexOf(image);
            new window.PhotoSwipe({
                dataSource: items,
                index: index >= 0 ? index : 0,
                showHideAnimationType: "zoom",
                closeSVG: IC_CLOSE,
                zoomSVG: IC_ZOOM,
                arrowPrevSVG: IC_ARROW,
                arrowNextSVG: IC_ARROW
            }).init();
        });
    });
}

if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(mountPhotoSwipe);
} else {
    document.addEventListener("DOMContentLoaded", mountPhotoSwipe);
}

})();
