export THUMBSDIR="screenshots_thumbs"
for screenshot in screenshots/*; do
	export filename=$(basename $screenshot);
	export output=("$THUMBSDIR/$filename");
	convert $screenshot -resize 600x355 $output;
	pngquant --force --skip-if-larger --speed 1 --verbose -o $output $output;
	
done