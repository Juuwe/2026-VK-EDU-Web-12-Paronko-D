document.addEventListener("DOMContentLoaded", () => {
    const configNode = document.getElementById('centrifugo-config');
    if (!configNode) return;

    const wsUrl = configNode.dataset.wsUrl;
    const token = configNode.dataset.token;
    const channel = configNode.dataset.channel;
    const currentPage = parseInt(configNode.dataset.currentPage, 10) || 1;
    const currentUser = configNode.dataset.currentUser;
    const questionAuthor = configNode.dataset.questionAuthor;

    if (!token) return;

    const centrifuge = new Centrifuge(wsUrl, { token });
    const sub = centrifuge.newSubscription(channel);

    sub.on('publication', (ctx) => {
        const data = ctx.data;

        if (data.author === currentUser) return;

        if (currentPage !== parseInt(data.target_page, 10)) {
            const goToNewPage = confirm(`Пользователь ${data.author} добавил новый ответ на страницу ${data.target_page}.\nПерейти к нему?`);

            if (goToNewPage) {
                window.location.href = `${window.location.pathname}?page=${data.target_page}`;
            }
            return;
        }

        const emptyStub = document.getElementById('no-answers-stub');
        if (emptyStub) emptyStub.remove();

        const answersList = document.getElementById('answers-list');
        if (!answersList) return;

        const firstNegativeAnswer = Array.from(answersList.children).find(el => {
            const rating = parseInt(el.dataset.rating, 10);
            return rating < 0;
        });

        if (firstNegativeAnswer) {
            firstNegativeAnswer.insertAdjacentHTML('beforebegin', data.html_template);
        } else {
            answersList.insertAdjacentHTML('beforeend', data.html_template);
        }

        if (currentUser === questionAuthor) {
            const hiddenCheckboxes = answersList.querySelectorAll('[data-ws-checkbox="true"].d-none');
            hiddenCheckboxes.forEach(cb => cb.classList.remove('d-none'));
        }
    });

    sub.subscribe();
    centrifuge.connect();
});
