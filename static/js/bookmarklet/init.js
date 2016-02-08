// JavaScript Document

var video_index = [],
	allow_video = false,
	patt = new RegExp("vi"),
	videos_not_on_youtube = [],
	min_size= {'w':150, 'h':150},
	latest  = {img:null, images:[], videos: []},
	is_youtube = new RegExp(/youtu\.be\/|youtube\.com/);

if(is_youtube.test(location.hostname)){
	allow_video = true;
	min_size= {'w':120, 'h':90};
	init_youtube_datas();
}else{
	var iframes = document.getElementsByTagName('iframe'),
		regex = /(youtu\.be\/|youtube\.com\/(watch\?(.*&)?v=|(embed|v)\/))([^\?&"'>]+)/;
	
	for (var i=0; i<iframes.length; i++){
		if(is_youtube.test(iframes[i].src)){
			videos_not_on_youtube[videos_not_on_youtube.length] = iframes[i].src.match(regex)[5];
		}
	}
}

(function () {
	
	//if(/^(www\.)?localhost$/.test(location.hostname)) return alert("installed. Go give it a try!");
	
	var prefix = 'bookmarklet-tagger-',
		iframe  = {obj: null, id: prefix + 'iframe', win: null, url: this.HOSTPATH},
		marker  = {obj: null, id: prefix + 'marker'},
		factory = document.createElement('div'),
		body    = document.body;

	extend(iframe, {
		show : function(){
			//Get all image have on the current page
			var im = document.images, i, c, imgs=[], idx=-1, data, videos=[];
			
			for(i=0,c=im.length; i < c; i++){
				
				var img_src = im[i].src;
				var naturalW = im[i].naturalWidth;
				var naturalH = im[i].naturalHeight;
				
				if(img_src!='' && (naturalW>=min_size.w || naturalH>=min_size.h)){
					
					if(latest.img && latest.img === im[i]){
						idx = imgs.length; 
					}
					var notfound_image = patt.test(img_src);
					
					if(allow_video & notfound_image){
						//Case all image url contain 'http://i1.ytimg.com/vi/[video_id]/default.jpg'
						var results = img_src.split("/"), 
							video_id = results[results.length-2];
						
						videos[imgs.length] = video_id;
						registerScript(video_id);
						video_index[video_id] = imgs.length;						
						
					}else if(allow_video & !notfound_image){
						//At view more video page, has 1 image is not found image which system saw
						//then set it become viewing image object.						
						var viewing_video_id = get_youtube_video_id(document.URL);
						if(viewing_video_id!=null){
							//update not-found image to viewing video thumb
							im[i].src = 'http://i1.ytimg.com/vi/'+viewing_video_id+'/hqdefault.jpg';
							
							videos[imgs.length] = viewing_video_id;
							registerScript(viewing_video_id);
							video_index[viewing_video_id] = imgs.length;
						}
					}
					
					imgs[imgs.length] = im[i];
				}
			}		
			
			//loop videos on the website not youtube
			for (var i=0; i<videos_not_on_youtube.length; i++){
				//init image object
				var img = document.createElement('img');
				//set video param value is video id
				videos[imgs.length] = videos_not_on_youtube[i];
				//get video info
				registerScript(videos_not_on_youtube[i]);
				//set video_index param value
				video_index[videos_not_on_youtube[i]] = imgs.length;
				
				imgs[imgs.length] = img;
			}
			
			//Update global data
			latest.images = imgs;
			latest.videos = videos;
			
			if(!latest.img || idx < 0) idx = 0;
			
			data = imageData(idx);
			
			this.obj.style.display = 'block';
			send(data);
		},
		hide : function(){
			this.obj.style.display = 'none';
			this.obj.setAttribute('src', 'about:blank');
		}	
	});
	
	extend(marker, {
		show : function(){
			if(this.obj) this.obj.style.display = 'block';
		},
		hide : function(){
			if(this.obj) this.obj.style.display = 'none';
		}
	});
	
	var handlers = {
		doc : {
			keyup : function(event){
				event = window.event || event;
				if(event.keyCode != 27) return; // exit if pressed key isn't ESC
	
				iframe.hide();
			},
			mouseover : function(event){
				event = window.event || event;
				var el = event.target || event.srcElement, pos;
	
				if(el.nodeName != 'IMG' || el.offsetWidth < 150 || el.offsetHeight < 150) return;
	
				latest.img = el;
	
				pos = offset(el);
				css(marker.obj, {top:pos.top+'px', left:pos.left+'px', width:el.offsetWidth+'px', height:el.offsetHeight+'px'});
				marker.show();
			}
		},
		marker : {
			click : function(event){
				event = window.event || event;
	
				try{
					event.preventDefault();
					event.stopPropagation();
				}catch(e){
					event.returnValue = false;
					event.cancelBubble = true;
				};
	
				iframe.show();
				marker.hide();
			},
			mouseout : function(event){
				event = window.event || event;
				var el = event.target || event.srcElement;
				if(el === marker.obj) marker.hide();
			}
		}
	};
	
	if('postMessage' in window){
		on(window, 'message', function(event){
			event = window.event || event;
			var args = unparam(event.data);
			onMessage(args);
		});
	} else {
		var hash = '', hashTimer = null;
		(function(){
			if(location.hash == hash || !/^#tagger:/.test(hash=location.hash)) return hashTimer=setTimeout(arguments.callee, 100);
			var args = unparam(hash.replace(/^#tagger:/, ''));
			onMessage(args);
		})();
	}
	
	function onMessage(args){
		switch(args.cmd){
			case 'close':
				iframe.hide();
				tagger.clean_listeners();
				break;
			case 'resize':
				iframe.obj.style.height = args.h+'px';
				break;
			case 'index':
				args.idx = parseInt(args.idx);
				data = imageData(args.idx);
				send(data);
				break;
		}
	};
	
	(function(){
		if(document.readyState !== 'complete') return setTimeout(arguments.callee, 100);
	
		// always create new iframe
		iframe.obj = elem(iframe.id);
		if(!iframe.obj) {
			
			factory.innerHTML = '<iframe id="'+iframe.id+'" scrolling="no" allowtransparency="true" style="display:none;position:fixed;top:0px;right:0px;border:1px solid #4c515c;z-index:99999999999999999;margin:0;background:#eff1f7;width:400px;height:450px;overflow:auto"></iframe>';
			iframe.obj = factory.lastChild;
			body.insertBefore(iframe.obj, body.firstChild);
			iframe.win = iframe.obj.contentWindow || iframe.obj;
			
		}
		iframe.show();
		// create a marker if it doesn't exist
		marker.obj = elem(marker.id);
		if(!marker.obj){
			factory.innerHTML = '<div id="'+marker.id+'" style="visibility:hidden;position:absolute;border:10px solid #8f0;z-index:100000;background:transparent url(http://s3.amazonaws.com/thefancy/_ui/images/f-plus.png) no-repeat 5px 5px"></div>';
			marker.obj = factory.lastChild;
			body.insertBefore(marker.obj, body.firstChild);
	
			css(marker.obj, {top:0, left:0});
			if(offset(marker.obj).top == 0) {
				css(marker.obj, {marginTop:'-10px',marginLeft:'-10px'});
			}
			css(marker.obj, {display:'none', visibility:'visible'});
		}
	
		each(handlers.doc, function(type,handler){ on(document, type, handler) });
		each(handlers.marker, function(type,handler){ on(marker.obj, type, handler) });
	})();
	
	var tagger = {
		clean_listeners : function(){
			each(handlers.doc, function(type,handler){ off(document, type, handler) });
			each(handlers.marker, function(type,handler){ off(marker.obj, type, handler) });
			clearTimeout(hashTimer);
		}
	};
	if(!window.thefancy_bookmarklet) window.thefancy_bookmarklet = {};
	
	window.thefancy_bookmarklet.tagger = tagger;

	// add event listsener to the specific element
	function on(el,type,handler){ el.attachEvent?el.attachEvent('on'+type,handler):el.addEventListener(type,handler,false) };
	
	// remove an event listener
	function off(el,type,handler){ el.detachEvent?el.detachEvent('on'+type,handler):el.removeEventListener(type,handler) };
	
	// get element by id
	function elem(id){ return document.getElementById(id) };
	
	// set css
	function css(el,prop){ for(var p in prop)if(prop.hasOwnProperty(p))try{el.style[p.replace(/-([a-z])/g,function(m0,m1){return m1.toUpperCase()})]=prop[p];}catch(e){} };
	
	// get offset
	function offset(el){ var t=0,l=0; while(el && el.offsetParent){ t+=el.offsetTop;l+=el.offsetLeft;el=el.offsetParent }; return {top:t,left:l} };
	
	// each
	function each(obj,fn){ for(var x in obj){if(obj.hasOwnProperty(x))fn.call(obj[x],x,obj[x],obj)} };
	
	// extend object like jquery's extend() function
	function extend(){ var a=arguments,i=1,c=a.length,o=a[0],x;for(;i<c;i++){if(typeof(a[i])!='object')continue;for(x in a[i])if(a[i].hasOwnProperty(x))o[x]=a[i][x]};return o };
	
	// unparam
	function unparam(s){ var a={},i,c;s=s.split('&');for(i=0,c=s.length;i<c;i++)if(/^([^=]+?)(=(.*))?$/.test(s[i]))a[RegExp.$1]=decodeURIComponent(RegExp.$3||'');return a };
	
	// send message to iframe window
	function send(data){ 
		iframe.obj.setAttribute('src', iframe.url+'#tagger:'+data);
		try{
			iframe.win.postMessage(data, this.HOSTPATH);
		}catch(e){
		} 
	};
	
	// image data
	function imageData(i){
		
		var imgs = latest.images, videos = latest.videos;
		
		var caption = 'video', video = videos[i];
		if(videos[i]=='undefined' || videos[i]=='' || videos[i]==null){
			caption = 'image';
			video = "null";
		}
		
		data = [
			'total='+imgs.length,
			'idx='+i,
			'loc='+encodeURIComponent(location.protocol+'//'+location.host+location.pathname+location.search),
			'caption='+caption,
			'video='+video
		];
		
		if(imgs[i]){
			data.push('src='+encodeURIComponent(imgs[i].src));
			data.push('title='+encodeURIComponent(imgs[i].getAttribute('alt') || imgs[i].getAttribute('title') || document.title));
		}
		
		return data.join('&');
	}
	
	//get youtube's video id
	function get_youtube_video_id( url){
		if(url === null){ return ""; }
		var results = url.match("[\\?&]v=([^&#]*)");
		return ( results === null ) ? null : results[1];
	}
	
	//get youtube's video thumbnail
	function get_youtube_video_thumbnail( url, size){
		if(url === null){ return ""; }		
		size = (size === null) ? "big" : size;		
		var results = url.match("[\\?&]v=([^&#]*)");
		var video_id = ( results === null ) ? url : results[1];
		if(size == "small"){
			return "http://img.youtube.com/vi/"+video_id+"/default.jpg";
		}else {
			return "http://img.youtube.com/vi/"+video_id+"/hqdefault.jpg";
		}
	}
	//register script to get video info
	function registerScript(videoId) {
		var s = document.createElement('script');
		s.type = 'text/javascript';
		s.src = 'https://gdata.youtube.com/feeds/api/videos/' + videoId + '?v=2&alt=jsonc&prettyprint=true&callback=videoInfoCallback';
		document.getElementsByTagName('head')[0].appendChild(s);
	}
	
})();


function init_youtube_datas(){
	var images = document.images;
	for(i=0, accept=0; i < images.length; i++){			
		var img_src = images[i].src;
		var naturalW = images[i].naturalWidth;
		var naturalH = images[i].naturalHeight;			
		if(img_src!='' && (naturalW >= 120 || naturalH >= 90) && patt.test(img_src) && accept==0){
			var alt = images[i].getAttribute('alt');
			if(alt=='Thumbnail' || alt==null || alt==''){
				///watch?v=p1JPKLa-Ofc
				var results = img_src.split("/"), video_id = results[results.length-2];
				var a = document.getElementsByTagName('a');
				var first_patt = new RegExp("[\\?&]v=" + video_id);
				
				for(k=0; k<a.length; k++){
					var href = a[k].getAttribute('href');
					var title = a[k].getAttribute('title');
					if(first_patt.test(href) && title){
						images[i].setAttribute('alt', title);
					}
				}
			}
			accept++;
		}
	}
}

function videoInfoCallback(info) {
	if (info.error) {
		return 'Error\n\n' + info.error.message;
	} else {
		var information = info.data;
		try {
			if (JSON && JSON.stringify) {
				//var information = JSON.stringify(info.data);
			}
		} catch (e) {
		}
		
		//Update image datas when finished callback of the get video info
		var imgs = latest.images;
		imgs[video_index[information.id]].src = information.thumbnail.hqDefault;
		imgs[video_index[information.id]].alt = information.title;
		
		return information;
	}
}