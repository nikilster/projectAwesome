App.Backbone.View.VisionDetailsComment = Backbone.View.extend({
    className: "VisionDetailsComment",
    sel: {
        LIKE: ".VisionLikeInfo",
    },
    initialize: function() {
        //_.bindAll(this, "gotoUser");
        this.urlTarget = this.options.urlTarget;
        this.render();
    },
    render: function() {
        var variables = { 'authorId' : this.model.authorId(),
                          'text': linkify(this.model.text()),
                          'name': this.model.name(),
                          'picture': this.model.picture(),
                          'urlTarget': this.urlTarget,
                          'created' : this.model.timeString(), }
        var template = _.template($("#VisionDetailsCommentTemplate").html(),
                                  variables);
        $(this.el).html(template);

        if (this.model.like() != null) {
            var likeView = new App.Backbone.View.Like(
                                                { model: this.model.like(),
                                                  parentView: this });
            $(this.el).find(this.sel.LIKE).append(likeView.el);
        }

        return this;
    },
});

