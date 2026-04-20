/**
 * App Entry Point — Initialize router and start the SPA
 */
document.addEventListener('DOMContentLoaded', () => {
    const router = new Router();

    router
        .on('/', () => pages.guard())
        .on('/register', () => pages.register())
        .on('/people', () => pages.people())
        .on('/phishing', () => pages.phishing())
        .on('/guard', () => pages.guard());

    router.start();
});
