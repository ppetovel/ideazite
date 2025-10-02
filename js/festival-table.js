function initFestivalTable(csvPath, opts){
  var EXCLUDE = ['festival','year','board image','board_image','boardimage'];
  function shouldShow(name){
    if(!name) return false;
    return EXCLUDE.indexOf(name.toLowerCase().trim()) === -1;
  }

  var AWARD_RANK = {
    "grand prix": 0,
    "titanium": 1,
    "gold": 2,
    "silver": 3,
    "bronze": 4,
    "shortlist": 5,
    "submitted": 6
  };
  function awardRankOf(val){
    var v = (val||"").toString().trim().toLowerCase();
    return (v in AWARD_RANK) ? AWARD_RANK[v] : 999;
  }

  Papa.parse(csvPath, {
    download:true, header:true, skipEmptyLines:true,
    complete:function(results){
      var rows = results.data || [];
      var fields = (results.meta && results.meta.fields) ? results.meta.fields : (rows.length ? Object.keys(rows[0]) : []);
      if(!fields.length) return;

      // Filtrar columnas según opts.columns
      var columnsToUse = (opts.columns && opts.columns.length) ? opts.columns : fields.filter(shouldShow);

      var columns = columnsToUse.map(function(name){
        var key = (name||'').toLowerCase().trim();
        if (opts.linkColumn && name === opts.linkColumn) {
          return {
            title: name, data: null,
            render: function(row){
              var t = row[name] || '';
              var url = row['Permalink'] || '';
              return (t && url) ? '<a class="title-link" href="'+url+'" rel="noopener">'+t+'</a>' : t;
            }
          };
        }
        if (key.indexOf('award') !== -1) {
          return {
            title: name, data: name,
            render: function(data, type){
              if (type === 'sort' || type === 'type') return awardRankOf(data);
              return data;
            }
          };
        }
        return { title: name, data: name };
      });

      $('#festivalTable').DataTable({
        data: rows,
        columns: columns,
        order: [[columns.findIndex(c=>c.title.toLowerCase().includes('award')), 'asc']],
        pageLength: 100,
        lengthMenu: [100,500,1000],
        scrollX: true,
        deferRender: true
      });
    }
  });
}
