use File::Path qw(make_path);

my $build_dir = 'build';
make_path($build_dir);

$do_cd = 0;
$out_dir = $build_dir;
$aux_dir = $build_dir;
$fdb_file = "$build_dir/$jobname.fdb_latexmk";
$emulate_aux_dir = 1;

push @generated_exts, 'spl';

my $bibinputs = $ENV{BIBINPUTS} // '';
$ENV{BIBINPUTS} = ".:$build_dir:$bibinputs";
