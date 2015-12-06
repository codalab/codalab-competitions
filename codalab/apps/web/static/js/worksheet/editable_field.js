/** @jsx React.DOM */

var EditableField = React.createClass({
  getInitialState: function() {
    return {};
  },
  componentDidMount: function() {
    $(this.refs.field.getDOMNode()).editable({
      send: 'always',
      type: 'text',
      mode: 'inline',
      value: this.props.value,
      url: '/api/worksheets/command/',
      params: function(params) {
        var data = {};
        var rawCommand = {};
        data['worksheet_uuid'] = this.props.wsUuid;
        rawCommand['k'] = this.props.fieldName;
        rawCommand['v'] = params['value'];
        rawCommand['action'] = 'worksheet-edit';
        data['raw_command'] = rawCommand;
        return JSON.stringify(data);
      }.bind(this),
      success: function(response, newValue) {
        if (response.exception) {
          return response.exception;
        }
        //this.props.refresh();
        this.props.onChange();
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
