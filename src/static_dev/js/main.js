$(document).ready(function(){
    const getCsrfToken = () => document.cookie.match(/csrftoken=([^;]+)/)?.[1];

    $(document).on('click', '.js-vote-btn', function(e) {
        e.preventDefault();
        const $btn = $(this);
        const $container = $btn.closest('.js-vote-container');

        $.ajax({
            url: `/${$container.data('type')}/${$container.data('id')}/like/`,
            type: 'POST',
            headers: { 'X-CSRFToken': getCsrfToken() },

            data: { value: $btn.data('value') },

            success: function(response) {
                if (response.status === 'ok') {
                    $container.find('.js-rating-value').text(response.new_rating);

                    const $iconLike = $container.find('.js-icon-like');
                    const $iconDislike = $container.find('.js-icon-dislike');

                    $iconLike.removeClass('text-success');
                    $iconDislike.removeClass('text-danger');

                    if (response.action === 'like') {
                        $iconLike.addClass('text-success');
                    } else if (response.action === 'dislike') {
                        $iconDislike.addClass('text-danger');
                    }
                }
            },

            error: function(xhr) {
                if (xhr.status === 401) {
                    window.location.href = '/login/?next=' + window.location.pathname;
                    return;
                }

                if (xhr.status === 403) {
                    alert("Сессия устарела. Пожалуйста, обновите страницу.");
                    return;
                }

                const errorMsg = xhr.responseJSON?.error || 'Что-то пошло не так...';
                alert(errorMsg);
            }
        });
    });

    $(document).on('change', '.js-correct-input', function() {
        const $input = $(this);
        const $container = $input.closest('.js-correct-container');

        const previousState = !$input.prop('checked');
        $input.prop('disabled', true);

        $.ajax({
            url: `/answer/${$container.data('id')}/correct/`,
            type: 'POST',
            headers: { 'X-CSRFToken': getCsrfToken() },

            success: function(response) {
                if (response.is_correct) {
                    $('.js-correct-input').not($input).prop('checked', false);
                }

                $input.prop('checked', response.is_correct);
            },

            error: function(xhr) {
                $input.prop('checked', previousState);

                if (xhr.status === 401) {
                    window.location.href = '/login/?next=' + window.location.pathname;
                    return;
                }

                if (xhr.status === 403) {
                    alert("Сессия устарела. Пожалуйста, обновите страницу.");
                    return;
                }

                const errorMsg = xhr.responseJSON?.error || 'Произошла ошибка';
                alert(errorMsg);
            },

            complete: function() {
                $input.prop('disabled', false);
            }
        });
    });
});
