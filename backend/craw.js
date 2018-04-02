//page ajax load:20
//single page max:

const puppeteer = require('puppeteer');

async function qqLogin(page, username, password) {
	const usrSelector = '#u';
	const pwdSelector = '#p';
	const submitSelector = '#login_button';
	
	await page.click('#otherLogin2 > li.w1.qq > a');
	await page.waitForNavigation();

	await console.log(page.url());//for check

	await page.click('#switcher_plogin');
	await page.type(usrSelector, username, {delay: 100});
	await page.type(pwdSelector, password, {delay: 100});
	await page.click(submitSelector);
	await page.waitForNavigation();
	await console.log(page.url());
}

async function telLogin(page, username, password) {
	const usrSelector = '#newlogin > div > div.contl-tel > div:nth-child(1) > input';
	const pwdSelector = '#newlogin > div > div.contl-tel > div:nth-child(2) > input';
	const submitSelector = '#newlogin > div > div.contl-tel > div.telnum-login';
	
	await page.click('#otherLogin2 > li.w1.tel > a');

	await page.type(usrSelector, username, {delay: 100});
	await page.type(pwdSelector, password);
	await page.click(submitSelector);
	await page.waitForNavigation();
	await console.log(page.url());
}

async function getFavoriteData(page) {
	// const likeSelector = '#rside > div:nth-child(1) > div > div.menum > ul > li:nth-child(3) > a'
	// await page.click(likeSelector);
	await page.goto('http://www.lofter.com/like?act=qbdashboardlike_20121221_01');
	await page.waitFor(8000);
	await console.log(page.url());

	var postList = await page.$$('.m-mlist');
	var lenBeforeLoad = postList.length;
	var lenAfterLoad = postList.length;
	while(true) { //single page load
		await page.evaluate(_ => {
			var mList = document.querySelectorAll('.m-mlist');
			mList[mList.length-1].scrollIntoView();
			mList[mList.length-1].scrollIntoView();
		});
		await page.waitFor(16000);
		postList = await page.$$('.m-mlist');
		lenAfterLoad = postList.length;
		if(lenAfterLoad == lenBeforeLoad) {
			console.log(lenAfterLoad);
			break;
		} else {
			lenBeforeLoad = lenAfterLoad;
		}
	}
	if(lenAfterLoad == 100) {
		var page = await page.$('.scrollList');
		if(page == null) {
			const errorStatus = "系统繁忙，请稍后再试\n";
			var endStatus = await page.$('.m-end')
			if(endStatus && endStatus.innerText == errorStatus) {
				console.log(endStatus.innerText);
			} else {
				await page.evaluate(_ => {
					window.scrollBy(0, document.body.scrollHeight);
				});
				page.screenshot({path: 'err.png'});
			}
		} else {
			var pageCount = page.children.length;
			var pageSelectorPre = '#pagerwidget > div > div > div.ui-3277803181.js-scrollList > div > div.scrollList.ztag > div:nth-child(';
			for(var i = 2; i <= pageCount; i++) {
				var pageSelector = pageSelectorPre + i + ')';
				await page.click(pageSelector);
				await page.waitFor(8000);
				var newPostList = await page.$$('.m-mlist');
				console.log(newPostList.length);
				postList = postList.concat(newPostList);
			}
		}
	}
}

(async () => {
	const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
	const page = await browser.newPage();
	await page.setDefaultNavigationTimeout(50000);
	await page.goto('http://www.lofter.com/login');
	await telLogin(page, '', '');
	await getFavoriteData(page);


	await browser.close();
})();