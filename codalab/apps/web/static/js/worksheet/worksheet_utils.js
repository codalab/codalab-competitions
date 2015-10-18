function render_permissions(state) {
  // Render permissions:
  // - state.permission_str (what user has)
  // - state.group_permissions (what other people have)
  var permission_str = 'you(' + state.permission_str + ')';
  permission_str += (state.group_permissions || []).map(function(perm) {
    return ' ' + perm.group_name + "(" + perm.permission_str + ")";
  }).join('');
  permission_str;
  return permission_str;
}

function shorten_uuid(uuid) {
  return uuid.slice(0, 8);
}
