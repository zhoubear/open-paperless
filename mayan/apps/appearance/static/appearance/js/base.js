'use strict';

var App = function (parameters) {
    var self = this;

    parameters = parameters || {}

    this.window = $(window);
}

App.tagSelectionTemplate = function (tag, container) {
  var $tag = $(
    '<span class="label label-tag" style="background: ' + tag.element.style.color + ';"> ' + tag.text + '</span>'
  );
  container[0].style.background = tag.element.style.color;
  return $tag;
}

App.tagResultTemplate = function (tag) {
  if (!tag.element) { return ''; }
  var $tag = $(
    '<span class="label label-tag" style="background: ' + tag.element.style.color + ';"> ' + tag.text + '</span>'
  );
  return $tag;
}

App.prototype.setupScrollView = function () {
    $('.scrollable').scrollview();
}

App.prototype.setupTableSelector = function () {
    $('th input:checkbox').click(function(e) {
        var table = $(e.target).closest('table');
        var checked = $(e.target).prop('checked');
        $('td input:checkbox', table).prop('checked', checked);
    });
}

App.prototype.setupWindowPopUp = function () {
    $('a.new_window').click(function(event) {
        event.preventDefault();
        var newWindow = window.open($(this).attr('href'), '_blank');
        newWindow.focus();
    });
}

App.prototype.setupSelect2 = function () {
    $('.select2').select2({
        dropdownAutoWidth: true,
        width: '100%'
    });

    $('.select2-tags').select2({
        templateSelection: App.tagSelectionTemplate,
        templateResult: App.tagResultTemplate,
        width: '100%'
    });
}

App.prototype.setupFullHeightResizing = function () {
    var self = this;

    this.resizeFullHeight();

    this.window.resize(function() {
        self.resizeFullHeight();
    });
}

App.prototype.resizeFullHeight = function () {
    $('.full-height').height(this.window.height() - $('.full-height').data('height-difference'));
}

App.prototype.doMessages = function () {
    // Add invisible bootstrap messages to copy the styles to toastr.js

    $('body').append('\
        <div class="hidden alert alert-success">\
            <p>text</p>\
        </div>\
        <div class="hidden alert alert-info">\
            <p>text</p>\
        </div>\
        <div class="hidden alert alert-danger">\
            <p>text</p>\
        </div>\
        <div class="hidden alert alert-warning">\
            <p>text</p>\
        </div>\
    ');

    // Copy the bootstrap style from the sample alerts to toaster.js via
    // dynamic document style tag

    $('head').append('\
        <style>\
            .toast-success {\
                background-color: ' + $('.alert-success').css('background-color') +'\
            }\
            .toast-info {\
                background-color: ' + $('.alert-info').css('background-color') +'\
            }\
            .toast-error {\
                background-color: ' + $('.alert-danger').css('background-color') +'\
            }\
            .toast-warning {\
                background-color: ' + $('.alert-warning').css('background-color') +'\
            }\
        </style>\
    ');

    $.each(DjangoMessages, function (index, value) {
        var options = {
            delay: 2000,
            type: value.tags,
            text: value.message,
            styling: 'bootstrap3',
        };

        if (value.tags === 'error') {
            // Error messages persist
            options['delay'] = 10000;
        }

        new PNotify(options);
    });
}

/* MayanImage class */

var MayanImage = function (options) {
    this.element = options.element;
    this.load();
}

MayanImage.intialize = function () {
    /*
    $('a.fancybox').fancybox({
        beforeShow : function(){
            this.title = $(this.element).data('caption');
        },
        openEffect  : 'elastic',
        closeEffect : 'elastic',
        prevEffect  : 'none',
        nextEffect  : 'none',
        titleShow   : true,
        type        : 'image',
        autoResize  : true,
    });
    */

   $('img.lazy-load').lazyload({
        appear: function(elements_left, settings) {
            new MayanImage({element: $(this)});
        },
        threshold: 400,
    });

    $('img.lazy-load-carousel').lazyload({
        appear: function(elements_left, settings) {
            new MayanImage({element: $(this)});
        },
        container: $('#carousel-container'),
        threshold: 2000
    });

    $('.lazy-load').on('load', function() {
        $(this).hide();
        $(this).fadeIn();
        $(this).siblings('.spinner-container').remove();
        $(this).removeClass('lazy-load pull-left');
    });

    $('.lazy-load-carousel').on('load', function() {
        $(this).hide();
        $(this).fadeIn();
        $(this).siblings('.spinner-container').remove();
        $(this).removeClass('lazy-load-carousel pull-left');
    });
}

MayanImage.prototype.onImageError = function () {
    this.element.parent().parent().html('<span class="fa-stack fa-lg"><i class="fa fa-file-o fa-stack-2x"></i><i class="fa fa-times fa-stack-1x text-danger"></i></span>');
    // Remove border to indicate non interactive image
    this.element.removeClass('thin_border');

    var container = this.element.parent().parent();
    // Save img HTML
    var html = this.element.parent().html();
    // Remove anchor
    this.element.parent().remove();
    // Place again img
    container.html(html);
};

MayanImage.prototype.load = function () {
    var self = this;

    this.element.error(function(event) {
        self.onImageError();
    });

    this.element.attr('src', this.element.attr('data-url'));
    $.fn.matchHeight._update();
    $.fn.matchHeight._maintainScroll = true;
};

jQuery(document).ready(function() {
    var app = new App();

    app.setupFullHeightResizing();

    MayanImage.intialize();

    app.doMessages();

    app.setupSelect2();

    app.setupScrollView();

    app.setupTableSelector();

    app.setupWindowPopUp();

    $('.select-auto-submit').change(function () {
        this.form.submit();
    });

    $('.checkbox-check-all-list-item').click(function(e) {
        var panel = $(e.target).parents('.x_panel');
        var checked = $(e.target).prop('checked');
        $('.x_content input:checkbox', panel).prop('checked', checked);
    });
});
