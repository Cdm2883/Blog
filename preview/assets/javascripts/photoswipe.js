(function () {

const IC_CLOSE = '<svg class="pswp__icn" viewBox="0 0 24 24" aria-hidden="true"><path fill="var(--pswp-icon-color)" d="M19 6.41 17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>';
const IC_ZOOM = '<svg class="pswp__icn" style="transform: scale(0.85)" viewBox="0 0 24 24" aria-hidden="true"><path fill="var(--pswp-icon-color)" d="M17 13h-4v4h-2v-4H7v-2h4V7h2v4h4m2-8H5c-1.11 0-2 .89-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2"/></svg>';
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
