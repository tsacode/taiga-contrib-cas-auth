var gulp = require('gulp');
var $ = require('gulp-load-plugins')();
var merge = require('merge-stream');

var paths = {
    jade: 'partials/*.jade',
    coffee: 'coffee/*.coffee',
    images: 'images/**/*',
    locales: 'locales/*.json',
    dist: 'dist/'
};

gulp.task('copy-config', function() {
    return gulp.src('cas-auth.json')
        .pipe(gulp.dest(paths.dist));
});

gulp.task('copy-images', function() {
    return gulp.src(paths.images)
        .pipe(gulp.dest(paths.dist + "images"));
});

gulp.task('copy-locales', function() {
    return gulp.src(paths.locales)
        .pipe(gulp.dest(paths.dist + "locales"));
});

gulp.task('compile', function() {
    var jade = gulp.src(paths.jade)
        .pipe($.plumber())
        .pipe($.cached('jade'))
        .pipe($.jade({pretty: true}))
        .pipe($.angularTemplatecache({
            transformUrl: function(url) {
                return '/plugins/cas-auth/' + url;
            }
        }))
        .pipe($.remember('jade'));

    var coffee = gulp.src(paths.coffee)
        .pipe($.plumber())
        .pipe($.cached('coffee'))
        .pipe($.coffee())
        .pipe($.remember('coffee'));

    return merge(jade, coffee)
        .pipe($.concat('cas-auth.js'))
        /*.pipe($.uglify({mangle:false, preserveComments: false}))*/
        .pipe(gulp.dest(paths.dist));
});

gulp.task('watch', function() {
    gulp.watch([paths.jade, paths.coffee, paths.images], ['copy-images', 'compile']);
});

gulp.task('default', ['copy-config', 'copy-images', 'compile', 'watch']);

gulp.task('build', ['copy-config', 'copy-images', 'compile', 'copy-locales' ]);
