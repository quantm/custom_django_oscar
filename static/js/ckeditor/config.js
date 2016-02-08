/**
 * @license Copyright (c) 2003-2013, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or http://ckeditor.com/license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here. For example:
	config.language = 'en';
	// config.uiColor = '#AADC6E';
	config.toolbar = 'Mini';
	config.toolbar_Mini =
	[
		{ name: 'basicstyles', items : [ 'Bold' , 'Italic' , 'Underline','Strike' , 'Subscript', 'Superscript'] }, '/',
		{ name: 'styles', items : [ 'Format' , 'Font' ] }, '/',
		{ name: 'colors', items : [ 'TextColor', 'BGColor' , 'FontSize' , '-' , 'RemoveFormat' ] } , '/',
		{ name: 'justify', items : [ 'JustifyLeft' , 'JustifyCenter' , 'JustifyRight' , 'JustifyBlock' ] }
	];
};
