const fs = require('fs');
let content = fs.readFileSync('/Users/lawrence/Workspace/lawrence-articles/post/2026-05-希腊别传/希腊别传.md', 'utf8');

// Extract the exact text we need to replace
const idx1 = content.indexOf('希罗多德写《历史》，不是记流水账');
const idx2 = content.indexOf('忘了该怎么想。」\n\n欧里庇得斯');
const actual = content.substring(idx1, idx2 + '忘了该怎么想。」'.length);

console.log('Actual text length:', actual.length);
console.log('First 50:', JSON.stringify(actual.substring(0, 50)));
console.log('Last 50:', JSON.stringify(actual.substring(actual.length - 50)));

// Write the actual text to compare
fs.writeFileSync('/tmp/actual_needle.txt', actual, 'utf8');
console.log('Written to /tmp/actual_needle.txt');

const replacement = `希罗多德写《历史》，不是记流水账，而是「研究」。

> history的本义是研究，有别于神话和传说的讲述，有别于意识形态的宣传，以这种研究态度来记述历史，正是从希罗多德开始的。
> ——第十二章 鼎盛的古典

修昔底德写《伯罗奔尼撒战争史》，记录条约原文，与后世考古出土的铭文若合符节。这是史学的诞生。

几何学不是用来测地，而是为了证明。

> 希腊人不断追问各种知识背后的为什么，探究事物终极的arche，终极原因或原理。围绕arche，各种知识组织成一个系统。这种系统知识，希腊人称之为episteme，或哲学-科学。episteme不以实用为目标，不单单无用于吃穿住行，而且也不能应用到修身养性，但希腊人却把episteme视作智性的最高追求，也只有希腊人才会去追求这种『为真理而真理』的episteme。
> ——第十二章 鼎盛的古典

> 几何学是系统知识的一个范例。这样一个系统侧重的不是一个三角形与某个三角形物体的联系，而是三角形的方方面面性质之间的联系；进一步，三角形的性质跟四边形、圆形、立方体、圆柱体的性质的联系。一片知识不是跟它的应用连在一起，而是跟另一片知识连在一起，最后连成一个知识系统。把这些知识连成整体的是证明。希腊人发明了证明。
> ——第十二章 鼎盛的古典

思想的自由需要言论的自由。

> 公民大会和审判法庭这类建制让希腊人习于公开辩论。尽管希腊人在很多方面成就卓异，研究希腊思想史的权威J. B. 伯里仍然断言：『希腊人首要也是最珍贵的成就当数无畏的思想自由。』
> ——第十二章 鼎盛的古典

伯里说的不是斯多葛那种内心自由——无论环境如何，思想可以在内心深处自由驰骋。

> 对鼎盛期的希腊人来说，心智的自由发展要求自由的表达。不讲，久而久之也就不敢想了，忘了该怎么想。
> ——第十二章 鼎盛的古典

欧里庇得斯`;

if (content.includes(actual)) {
  content = content.replace(actual, replacement);
  fs.writeFileSync('/Users/lawrence/Workspace/lawrence-articles/post/2026-05-希腊别传/希腊别传.md', content, 'utf8');
  console.log('SUCCESS: 古典时代 part 1 done');
} else {
  console.log('FAILED: text not found');
  fs.writeFileSync('/tmp/actual.txt', actual, 'utf8');
}