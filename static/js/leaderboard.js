$(document).ready(function(){
  $('#refresh-btn').click(function() {
    $('#table').bootstrapTable('refresh');
    alert('refreshed');
  })
})
$('#table').bootstrapTable({
    url: 'http://localhost:5000/users/json',
    columns: [{
        field: 'name',
        title: 'Name'
    }, {
        field: 'count',
        title: 'Connections'
    },]
});
