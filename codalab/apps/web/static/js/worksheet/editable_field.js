/** @jsx React.DOM */

var EditableField = React.createClass({
  propTypes: {
    value: React.PropTypes.string,
    url: React.PropTypes.string.isRequired,
    buildParams: React.PropTypes.func.isRequired,
    onChange: React.PropTypes.func,
    canEdit: React.PropTypes.bool.isRequired
  },
  componentDidMount: function() {
    $(this.refs.field.getDOMNode()).editable({
      send: 'always',
      type: 'text',
      mode: 'inline',
      value: this.props.value,
      url: this.props.url,
      defaultValue: '<none>',
      params: function(params) {
        return JSON.stringify(this.props.buildParams(params));
      }.bind(this),
      success: function(response, newValue) {
        if (response.exception) {
          return response.exception;
        }
        if ('onChange' in this.props) {
          this.props.onChange();
        }
      }.bind(this)
    }).on('click', function() {
      // Hack to put the right input into the field, since the jQuery plugin doesn't update it properly
      // in response to new values.
      if (!this.props.canEdit) return;
      $(this.refs.field.getDOMNode()).data('editable').input.value2input(this.props.value);
    }.bind(this));
  },
  componentDidUpdate: function() {
    //$(this.refs.field.getDOMNode()).editable('option', 'value', this.props.value);
    $(this.refs.field.getDOMNode()).editable('option', 'disabled', !this.props.canEdit);
  },
  render: function () {
    return (
      <a href="#" ref='field'>{this.props.value}</a>
    );
  }
});

var WorksheetEditableField = React.createClass({
  propTypes: {
    uuid: React.PropTypes.string,
    fieldName: React.PropTypes.string
  },
  buildParams: function(params) {
    return {
      worksheet_uuid: this.props.uuid,
      raw_command: {
        k: this.props.fieldName,
        v: params.value,
        action: 'worksheet-edit'
      }
    };
  },
  render: function () {
    return (
      <EditableField {...this.props} url="/api/worksheets/command/" buildParams={this.buildParams} />
    );
  }
});

var BundleEditableField = React.createClass({
  propTypes: {
    uuid: React.PropTypes.string,
    metadata: React.PropTypes.object,
    fieldName: React.PropTypes.string
  },
  buildParams: function(params) {
    var metadata = _.clone(this.props.metadata);
    metadata[this.props.fieldName] = params.value;
    return {
      metadata: metadata
    };
  },
  render: function () {
    return (
      <EditableField {...this.props} value={String(this.props.metadata[this.props.fieldName])} url={"/api/bundles/" + this.props.uuid + "/"} buildParams={this.buildParams} />
    );
  }
});
