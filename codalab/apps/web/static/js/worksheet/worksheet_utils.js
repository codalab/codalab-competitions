function render_permissions(state) {
  // Render permissions:
  // - state.permission_str (what user has)
  // - state.group_permissions (what other people have)
  var permission_str = state.permission_str + ' [';
  permission_str += (state.group_permissions || []).map(function(perm) {
    perm.group_name + "(" + perm.permission_str + ")";
  }).join(' ');
  permission_str += ']';
  return permission_str;
}
