/** @typedef {'fraud' | 'suspicious' | 'safe' | 'spam'} ClassificationTone */

/** @typedef {{
 *   id: string;
 *   sender: string;
 *   subject: string;
 *   classification: string;
 *   tone: ClassificationTone;
 *   received: string;
 *   confidence?: number;
 *   reasons?: string[];
 *   rules?: string[];
 * }} InboxEmail */

/** @type {InboxEmail[]} */
export const inboxEmails = [
	{
		id: '1',
		sender: 'paypal-secure-alert.com',
		subject: 'Your account has been limited',
		classification: 'Fraud',
		tone: 'fraud',
		received: '9:14 AM',
		confidence: 98,
		reasons: [
			'Domain is 4 days old, not the verified PayPal domain',
			"Link destination doesn't match displayed text",
			'Urgency language matches known phishing patterns'
		],
		rules: ['Spoofed brand domain']
	},
	{
		id: '2',
		sender: 'Unknown sender',
		subject: 'Invoice #4471 attached',
		classification: 'Suspicious',
		tone: 'suspicious',
		received: '8:52 AM',
		confidence: 72,
		reasons: ['Sender domain has no prior history', 'Attachment type commonly used in phishing'],
		rules: ['Unknown sender with attachment']
	},
	{
		id: '3',
		sender: 'Sarah Chen',
		subject: 'Re: Q3 planning doc',
		classification: 'Safe',
		tone: 'safe',
		received: '8:41 AM',
		confidence: 99,
		reasons: ['Known contact with verified domain'],
		rules: []
	},
	{
		id: '4',
		sender: 'Linear',
		subject: '3 issues assigned to you',
		classification: 'Safe',
		tone: 'safe',
		received: '7:30 AM',
		confidence: 97,
		reasons: ['Verified notification sender'],
		rules: []
	},
	{
		id: '5',
		sender: 'newsletter@deals.io',
		subject: '50% off everything this weekend',
		classification: 'Spam',
		tone: 'spam',
		received: '6:02 AM',
		confidence: 91,
		reasons: ['Bulk marketing patterns detected'],
		rules: ['Promotional bulk sender']
	}
];
