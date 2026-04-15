/**
 * Simple Hash Router for SPA navigation
 */
class Router {
    constructor() {
        this.routes = {};
        this.currentPage = null;
        window.addEventListener('hashchange', () => this.resolve());
    }

    on(path, handler) {
        this.routes[path] = handler;
        return this;
    }

    resolve() {
        const hash = window.location.hash.slice(1) || '/';
        const handler = this.routes[hash] || this.routes['/'];

        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.toggle('active', link.getAttribute('href') === `#${hash}`);
        });

        // Clean up previous page
        if (this.currentPage && this.currentPage.destroy) {
            this.currentPage.destroy();
        }

        if (handler) {
            this.currentPage = handler();
        }
    }

    start() {
        this.resolve();
    }
}

window.Router = Router;
