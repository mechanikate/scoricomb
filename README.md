<h1 align="center">scoricomb</h1>
A Python script to calculate every single way an NFL score can be reached.
For an example of what this does, a 6-0 final score can be achieved with:
<ol>
    <li>
        <ul>
            <li>Field goal</li>
            <li>Field goal</li>
        </ul>
    </li>
    <li>
        <ul>
            <li>Touchdown with no extra points</li>
        </ul>
    </li>
    <li>
        <ul>
            <li>Safety</li>
            <li>Safety</li>
            <li>Safety</li>
        </ul>
    </li>
</ol>
This would be calculated as:
<br />
<code>[([3,3],[0,0]),([2,2,2],[0,0,0]),([6],[0])]</code>
<br />
There are also options to cache some "base" scoring permutations, trading storage space (a couple megabytes) for speed & performance. It is <u>highly recommended</u> to run the <code>presave_scores.py</code> script!
