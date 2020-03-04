var colors_suggestions = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.whitespace,
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  // prefetch: 'http://127.0.0.1:5000/colors',
  // remote: 'http://127.0.0.1:5000/remote'
  remote: {
    url: 'http://127.0.0.1:5000/typeahead?q=%QUERY',
    wildcard: '%QUERY'
  },
  // remote: {
  //   url: 'http://127.0.0.1:5000/test?query=%QUERY',
  //   wildcard: '%QUERY'
  // },

  // local: ['Red','Blood Red','White','Blue','Yellow','Green','Black','Pink','Orange', 'Super og kush', 'og kush', 'Purple og kush']
  // local: [{'value': 'Red'},
  //     {'value': 'Blood Red'},
  //     {'value': 'White'},
  //     {'value': 'Blue'},
  //     {'value': 'Yellow'},
  //     {'value': 'Green'},
  //     {'value': 'Black'},
  //     {'value': 'Pink'},
  //     {'value': 'Orange'}],

});

// init Typeahead
$('#my_search').typeahead({
  hint: true,
  highlight: true,
  minLength: 2
},
{
  name: 'colors',
  source: colors_suggestions,   // suggestion engine is passed as the source
  templates: {
    notFound: '<div>Not Found</div>',   /* Rendered if 0 suggestions are available */
    pending: '<div>Loading...</div>',   /* Rendered if 0 synchronous suggestions available
                                           but asynchronous suggestions are expected */
    header: '<div>Found Records:</div>',/* Rendered at the top of the dataset when
                                           suggestions are present */
    suggestion:  function(data) {       /* Used to render a single suggestion */
                    return '<div><a href="/name_to_index?name=' + data + '">'+ data +'</a></div>'
                 },
    footer: function (query) {
              // return '<div><a href="/search/'  + query.query + '">Search: ' + query.query + '</a></div>'
              return '<div><a href="/strains?filter=search&q='  + query.query + '">Search: ' + query.query + '</a></div>'
    }
}
});