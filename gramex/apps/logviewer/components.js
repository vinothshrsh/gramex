// Usage: $('.card-load-time').logviewer(config)


$.fn.logviewer = function (config) {
  this.each(function () {
    var url = 'log/query/aggD/kpi-pageviews/?time%3E~=2020-08-27%2000%3A00%3A00&time%3C~=2020-09-25%2000%3A00%3A00'
    $.get(url)
      .done(console.log)
      .fail(console.log)


  })
}
