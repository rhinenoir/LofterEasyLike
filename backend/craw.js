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
}

async function telLogin(page, username, password) {
	const usrSelector = '#newlogin > div > div.contl-tel > div:nth-child(1) > input';
	const pwdSelector = '#newlogin > div > div.contl-tel > div:nth-child(2) > input';
	const submitSelector = '#newlogin > div > div.contl-tel > div.telnum-login';
	
	await page.click('#otherLogin2 > li.w1.tel > a');

	await page.type(usrSelector, username, {delay: 100});
	await page.type(pwdSelector, password, {delay: 100});
	await page.click(submitSelector);
	await page.waitForNavigation();
}

(async () => {
	const browser = await puppeteer.launch({ args: ['--no-sandbox', '--disable-setuid-sandbox'] });
	const page = await browser.newPage();
	await page.goto('http://www.lofter.com/login');
	await telLogin(page, 'xxxxx', 'yyyyy');
	await console.log(page.url());
	await browser.close();
})();