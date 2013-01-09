App.Backbone.View.VisionDetailsComment = Backbone.View.extend({
    className: "VisionDetailsComment",
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

        return this;
    },
});

