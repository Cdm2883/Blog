// noinspection JSUnresolvedReference,JSIgnoredPromiseFromCall,ES6ConvertVarToLetConst

document$.subscribe(function() {
    var tables = document.querySelectorAll("article table:not([class])")
    tables.forEach(function(table) {
        new Tablesort(table)
    })
})
