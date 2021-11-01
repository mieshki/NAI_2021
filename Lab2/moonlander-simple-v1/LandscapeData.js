
function Landscape(){
	
	var points = this.points = [],
		lines = this.lines = [], 
		stars = this.stars = [],
	 	availableZones = [], 
		zoneCombis = [], 
		currentCombi = 0, 
		zoneInfos = [], 
		landscale = 1.5, 
		rightedge, 
		flickerProgress = 0;
		
	setupData(); 


	rightedge = this.tileWidth = points[points.length - 1].x * landscale ;
	
	for (var i = 0; i<points.length; i++){
		var p = points[i];
		p.x *= landscale;
		p.y *= landscale;
		p.y -= 50;

	}
	
	for(var i = 1;i < points.length; i++){
		var p1 = points[i-1];
		var p2 = points[i]; 
		lines.push(new LandscapeLine(p1, p2));
	}

	
	// make stars... 
	
	
	
	for(var i = 0;i < lines.length;i++)	{
		if(Math.random() < 0.1) {
			var line  = lines[i];
			
			var star = { x:line.p1.x, y: Math.random() *600 };
	
			if((star.y < line.p1.y) && (star.y < line.p2.y)) {
				stars.push(star);
			}
		}
	}	

		
	//	var pointcount = points.length;

		//var dirtyRectangles = []; 

	
	
	var render = this.render = function(c, view) { 

		var offset = 0; 
		
		while(view.left-offset>rightedge) { 
			offset+=rightedge; 
		}
		
		while(view.left-offset<0) { 
			offset-=rightedge;
		}
		
		var startOffset = offset; 
		
		var i = 0; 
		
		while(lines[i].p2.x+offset<view.left) { 
			i++; 
			if(i>lines.length) {
				i=0; 
				offset+=rightedge; 
			}
		}
		
		c.beginPath(); 
		
		var line = lines[i];
		var offsetY = 0; 
		if(Math.random()<0.3) { 
			offset+=(0.2/view.scale); 
			offsetY = (0.2/view.scale); 
		}
		c.moveTo(line.p1.x + offset, line.p1.y + offsetY);  
		
		var zoneInfoIndex = 0; 

		while((line = lines[i]).p1.x+offset<view.right) { 
			
			var point = line.p2; 
			c.lineTo(point.x+offset, point.y);
			
			if((counter%20>10) && (line.multiplier!=1)){ 
				var infoBox; 
				
				if(!zoneInfos[zoneInfoIndex]) { 
					infoBox = zoneInfos[zoneInfoIndex] = new InfoBox(1,50); 
					document.body.appendChild(infoBox.domElement); 
				} else {
					infoBox = zoneInfos[zoneInfoIndex]; 
					infoBox.show(); 
				}
				infoBox.setText(line.multiplier+'x'); 
				infoBox.setX(((((line.p2.x-line.p1.x)/2)+line.p1.x+offset)*view.scale)+view.x); 
				infoBox.setY(((line.p2.y+2) *view.scale)+view.y); 
				zoneInfoIndex++; 
				
			}
			
			i++; 
			if(i>=lines.length) {
				i=0; 
				offset+=rightedge; 
			}
			
	
		}
		
		var flickerAmount = Math.sin(counter*0.8)*0.5 + 0.5; 
		
		if(flickerAmount>0.5) { 
					c.lineWidth = 2/view.scale; 
					var channel = Math.round((flickerAmount-0.5)*(100)); 
				  	c.strokeStyle = "rgb("+channel+","+channel+","+channel+")";
					c.stroke(); 
					
				}	
		c.strokeStyle = 'white'; 
		
		
		c.lineWidth = 1/view.scale * (flickerAmount*0.2+0.8); 
		c.lineJoin = 'bevel';
		c.stroke();	
		
		
		for(var i=zoneInfoIndex; i<zoneInfos.length; i++) { 
			zoneInfos[i].hide(); 
		}
		
		
		// draw stars : 
		
		/*	
		i = 0; 
		offset = startOffset;
		
		while(stars[i].x+offset<view.left) { 
			i++; 
			if(i>=stars.length) {
				i=0; 
				offset+=rightedge; 
			}
		}
		
		c.beginPath(); 
		
		while((star = stars[i]).x+offset<view.right) { 
		
			var starx = star.x+offset; 
			var stary = star.y; 
			while(view.bottom<stary) stary-=600; 
			
			c.rect(starx, stary, (1/view.scale),(1/view.scale));
			if(stary-600>view.top) { 
				stary-=600; 
				c.rect(starx, stary, (1/view.scale),(1/view.scale));
				
			}
			
			i++; 
			if(i>=stars.length) {
				i=0; 
				offset+=rightedge; 
			}
		
		
		}		
		*/
		c.stroke(); 
		
		
		//code to check landable... 
		 c.beginPath(); 
		 for(var i=0; i<lines.length; i++) { 
		 	var line = lines[i]; 
		 	if(line.checked) { 
		 		c.moveTo(line.p1.x, line.p1.y);	
		 		c.lineTo(line.p2.x, line.p2.y);
		 		
		 		if(line.p2.x+rightedge < view.right) { 
		 				c.moveTo(line.p1.x+rightedge, line.p1.y);	
		 				c.lineTo(line.p2.x+rightedge, line.p2.y);
		 			
		 		}
		 	}		
		 }	
		 c.strokeStyle = 'red'; 
		 c.stroke(); 
	
	};
	
	this.setZones = function () { 

		for (var i=0; i<lines.length; i++)
		{
			lines[i].multiplier = 1;
		}	

		var combi = zoneCombis[currentCombi];
		console.log('zoneCombis: ' + zoneCombis)
		console.log('currentCombi: ' + currentCombi)

		for (var i = 0; i<combi.length; i++)
		{
			var zonenumber = combi[i];
			console.log('zonenumber: ' + zonenumber)
			var zone = availableZones[zonenumber];
			line = lines[zone.lineNum];

			// var zoneLabel : TextDisplay = zoneLabels[i]; 
			// 		zoneLabel.x = line.p1.x + ((line.p2.x - line.p1.x) / 2);
			// 		zoneLabel.y = line.p1.y;
			// 		zoneLabel.text = zone.multiplier + "X";
			line.multiplier = zone.multiplier;

		}

		currentCombi++;
		if(currentCombi >= zoneCombis.length) currentCombi = 0;
	};


		
	
	function setupData() { 
	/*
	original:
		points.push(new Vector2(0.5, 409.5));
		points.push(new Vector2(51.75, 409.5));
		points.push(new Vector2(151.75, 409.5));
		points.push(new Vector2(251.75, 409.5));
		points.push(new Vector2(351.75, 409.5));
		points.push(new Vector2(451.75, 409.5));
		points.push(new Vector2(851.75, 409.5));
		points.push(new Vector2(951.75, 409.5));
	
	*/
	
		points.push(new Vector2(0.5, 409.5));
		points.push(new Vector2(51.75, 409.5));
		points.push(new Vector2(151.75, 409.5));
		points.push(new Vector2(251.75, 409.5));
		points.push(new Vector2(351.75, 409.5));
		points.push(new Vector2(451.75, 409.5));
		points.push(new Vector2(851.75, 409.5));
		points.push(new Vector2(951.75, 409.5));
		
		console.log('points length:' + points.length)
		
		availableZones.push(new LandingZone(0, 2));
		availableZones.push(new LandingZone(1, 2));
		availableZones.push(new LandingZone(2, 2));
		availableZones.push(new LandingZone(3, 2));
		availableZones.push(new LandingZone(4, 2));
		availableZones.push(new LandingZone(5, 2));
		//availableZones.push(new LandingZone(6, 2));
		/*availableZones.push(new LandingZone(13, 3));
		availableZones.push(new LandingZone(25, 4));
		availableZones.push(new LandingZone(34, 4));		
		availableZones.push(new LandingZone(63, 5));	
		availableZones.push(new LandingZone(75, 4));	
		availableZones.push(new LandingZone(106, 5));	
		availableZones.push(new LandingZone(111, 2));	
		availableZones.push(new LandingZone(121, 5));	
		availableZones.push(new LandingZone(133, 2));*/	
		//availableZones.push(new LandingZone(148, 3));
		
			
		zoneCombis.push([0]); // - modified
		//zoneCombis.push([2,3,7,9]);  // - org
		/*zoneCombis.push([7,8,9,10]);
		zoneCombis.push([2,3,7,9]);
		zoneCombis.push([1,4,7,9]);
		zoneCombis.push([0,5,7,9]);
		zoneCombis.push([6,7,8,9]);
		zoneCombis.push([1,4,7,9]);*/
	}

	
}; 

function LandscapeLine(p1, p2) { 
	this.p1 = p1; 
	this.p2 = p2; 
	this.landable = (p1.y==p2.y); 
	this.multiplier = 1; 
	
}

function LandingZone(linenum, multi) {
	
	this.lineNum = linenum; 
	this.multiplier = multi; 
}