import {
	Box3,
	Line3,
	Plane,
	Sphere,
	Triangle,
	Vector3
} from 'three';
import { Capsule } from './Capsule.js';


const _v1 = new Vector3();
const _v2 = new Vector3();
const _plane = new Plane();
const _line1 = new Line3();
const _line2 = new Line3();
const _sphere = new Sphere();
const _capsule = new Capsule();

class Octree {


	constructor( box ) {

		this.triangles = [];
		this.box = box;
		this.subTrees = [];

	}

	addTriangle( triangle ) {

		if ( ! this.bounds ) this.bounds = new Box3();

		this.bounds.min.x = Math.min( this.bounds.min.x, triangle.a.x, triangle.b.x, triangle.c.x );
		this.bounds.min.y = Math.min( this.bounds.min.y, triangle.a.y, triangle.b.y, triangle.c.y );
		this.bounds.min.z = Math.min( this.bounds.min.z, triangle.a.z, triangle.b.z, triangle.c.z );
		this.bounds.max.x = Math.max( this.bounds.max.x, triangle.a.x, triangle.b.x, triangle.c.x );
		this.bounds.max.y = Math.max( this.bounds.max.y, triangle.a.y, triangle.b.y, triangle.c.y );
		this.bounds.max.z = Math.max( this.bounds.max.z, triangle.a.z, triangle.b.z, triangle.c.z );

		this.triangles.push( triangle );

		return this;

	}

	calcBox() {

		this.box = this.bounds.clone();

		// offset small ammount to account for regular grid
		this.box.min.x -= 0.01;
		this.box.min.y -= 0.01;
		this.box.min.z -= 0.01;

		return this;

	}
   
	split( level ) {

		if ( ! this.box ) return;
        
		const subTrees = [];
		const halfsize = _v2.copy( this.box.max ).sub( this.box.min ).multiplyScalar( 0.5 );

		// 3D空间分割为8个子空间
		for ( let x = 0; x < 2; x ++ ) {

			for ( let y = 0; y < 2; y ++ ) {

				for ( let z = 0; z < 2; z ++ ) {
                    // 每个子空间用一个包围盒表示
					const box = new Box3();
					const v = _v1.set( x, y, z );

					box.min.copy( this.box.min ).add( v.multiply( halfsize ) );
					box.max.copy( box.min ).add( halfsize );
                    // 包围盒创建一个八叉图Octree
					subTrees.push( new Octree( box ) );

				}

			}

		}

		let triangle;

		while ( triangle = this.triangles.pop() ) {

			for ( let i = 0; i < subTrees.length; i ++ ) {

				if ( subTrees[ i ].box.intersectsTriangle( triangle ) ) {

					subTrees[ i ].triangles.push( triangle );

				}

			}

		}

		for ( let i = 0; i < subTrees.length; i ++ ) {

			const len = subTrees[ i ].triangles.length;

			// if ( len > 8 && level < 16 ) {
			if ( len > 8 && level < 16 ) {//修改八叉树深度和顶点数量划分

				subTrees[ i ].split( level + 1 );

			}

			if ( len !== 0 ) {

				this.subTrees.push( subTrees[ i ] );

			}

		}

		return this;

	}

	build() {
        // 计算包围盒
		this.calcBox();
		this.split( 0 );

		return this;

	}

	getRayTriangles( ray, triangles ) {

		for ( let i = 0; i < this.subTrees.length; i ++ ) {

			const subTree = this.subTrees[ i ];
			// 射线和八叉树某个节点对应的包围盒box进行计算
			if ( ! ray.intersectsBox( subTree.box ) ) continue;

			if ( subTree.triangles.length > 0 ) {

				for ( let j = 0; j < subTree.triangles.length; j ++ ) {

					if ( triangles.indexOf( subTree.triangles[ j ] ) === - 1 ) triangles.push( subTree.triangles[ j ] );

				}

			} else {
                // 如果没有三角形，说明不是叶子节点，再继续获取，递归遍历
				subTree.getRayTriangles( ray, triangles );

			}

		}

		return triangles;

	}

	// 与三角形交叉计算
	triangleCapsuleIntersect( capsule, triangle ) {

		// 通过三角形获取一个平面
		triangle.getPlane( _plane );

		// 两个球心与平面的距离减去半径
		const d1 = _plane.distanceToPoint( capsule.start ) - capsule.radius;
		const d2 = _plane.distanceToPoint( capsule.end ) - capsule.radius;

		// d1、d2都大于零  意味着没有碰撞
		if ( ( d1 > 0 && d2 > 0 ) || ( d1 < - capsule.radius && d2 < - capsule.radius ) ) {

			return false;

		}

		//交叉点与起始点相对百分比
		const delta = Math.abs( d1 / ( Math.abs( d1 ) + Math.abs( d2 ) ) );
		// 计算胶囊竖直线与场景交叉点
		// 所谓的交叉点，并不是半球面与mesh交叉，而是上面一个点
		// 交叉点：轴线与三角形的交叉点  计算方式
		const intersectPoint = _v1.copy( capsule.start ).lerp( capsule.end, delta );

		// 交叉点在三角形内部
		if ( triangle.containsPoint( intersectPoint ) ) {

			// 三角形的法线作为平面的法线
			// 获取三角形对应平面的法线，作为交叉法线   法线用来调整姿态
			// 交叉面深度
			// 感觉是可行的
			// 运动过程中，一旦算出来交叉，就拔出来
			return { normal: _plane.normal.clone(), point: intersectPoint.clone(), depth: Math.abs( Math.min( d1, d2 ) ) };

		}

		const r2 = capsule.radius * capsule.radius;

		// 创建一个Line3线段
		const line1 = _line1.set( capsule.start, capsule.end );

		// 三角形三条边，创先三个线段
		const lines = [
			[ triangle.a, triangle.b ],
			[ triangle.b, triangle.c ],
			[ triangle.c, triangle.a ]
		];

		for ( let i = 0; i < lines.length; i ++ ) {

			const line2 = _line2.set( lines[ i ][ 0 ], lines[ i ][ 1 ] );

			const [ point1, point2 ] = capsule.lineLineMinimumPoints( line1, line2 );

			// 点1与点2距离与半径比较，小于半径，说明存在交叉，点2作为交叉点
			if ( point1.distanceToSquared( point2 ) < r2 ) {

				return { normal: point1.clone().sub( point2 ).normalize(), point: point2.clone(), depth: capsule.radius - point1.distanceTo( point2 ) };

			}

		}

		return false;

	}

	triangleSphereIntersect( sphere, triangle ) {

		triangle.getPlane( _plane );

		if ( ! sphere.intersectsPlane( _plane ) ) return false;

		const depth = Math.abs( _plane.distanceToSphere( sphere ) );
		const r2 = sphere.radius * sphere.radius - depth * depth;

		const plainPoint = _plane.projectPoint( sphere.center, _v1 );

		if ( triangle.containsPoint( sphere.center ) ) {

			return { normal: _plane.normal.clone(), point: plainPoint.clone(), depth: Math.abs( _plane.distanceToSphere( sphere ) ) };

		}

		const lines = [
			[ triangle.a, triangle.b ],
			[ triangle.b, triangle.c ],
			[ triangle.c, triangle.a ]
		];

		for ( let i = 0; i < lines.length; i ++ ) {

			_line1.set( lines[ i ][ 0 ], lines[ i ][ 1 ] );
			_line1.closestPointToPoint( plainPoint, true, _v2 );

			const d = _v2.distanceToSquared( sphere.center );

			if ( d < r2 ) {

				return { normal: sphere.center.clone().sub( _v2 ).normalize(), point: _v2.clone(), depth: sphere.radius - Math.sqrt( d ) };

			}

		}

		return false;

	}

	getSphereTriangles( sphere, triangles ) {

		for ( let i = 0; i < this.subTrees.length; i ++ ) {

			const subTree = this.subTrees[ i ];

			if ( ! sphere.intersectsBox( subTree.box ) ) continue;

			if ( subTree.triangles.length > 0 ) {

				for ( let j = 0; j < subTree.triangles.length; j ++ ) {

					if ( triangles.indexOf( subTree.triangles[ j ] ) === - 1 ) triangles.push( subTree.triangles[ j ] );

				}

			} else {

				subTree.getSphereTriangles( sphere, triangles );

			}

		}

	}

	getCapsuleTriangles( capsule, triangles ) {

		// 递归遍历整个八叉树
		for ( let i = 0; i < this.subTrees.length; i ++ ) {

			const subTree = this.subTrees[ i ];

			// 判断当前包围盒节点是否和胶囊几何体重合
			if ( ! capsule.intersectsBox( subTree.box ) ) continue;

			// 如果重合判断下有没有子对象包围盒，如果有继续，继续递归遍历
			if ( subTree.triangles.length > 0 ) {

				for ( let j = 0; j < subTree.triangles.length; j ++ ) {

					if ( triangles.indexOf( subTree.triangles[ j ] ) === - 1 ) triangles.push( subTree.triangles[ j ] );

				}

			} else {

				// 没有的话，叶子节点，就把该包围盒的所有三角形与
				subTree.getCapsuleTriangles( capsule, triangles );

			}

		}

	}

	sphereIntersect( sphere ) {

		_sphere.copy( sphere );

		const triangles = [];
		let result, hit = false;

		this.getSphereTriangles( sphere, triangles );

		for ( let i = 0; i < triangles.length; i ++ ) {

			if ( result = this.triangleSphereIntersect( _sphere, triangles[ i ] ) ) {

				hit = true;

				_sphere.center.add( result.normal.multiplyScalar( result.depth ) );

			}

		}

		if ( hit ) {

			const collisionVector = _sphere.center.clone().sub( sphere.center );
			const depth = collisionVector.length();

			return { normal: collisionVector.normalize(), depth: depth };

		}

		return false;

	}
    // 八叉树与胶囊射线拾取计算
	capsuleIntersect( capsule ) {

		// 新复制一个_capsule
		_capsule.copy( capsule );

		const triangles = [];
		let result, hit = false;

		this.getCapsuleTriangles( _capsule, triangles );

		// 计算包围盒内，所有的三角形与胶囊碰撞体的碰撞检测
		for ( let i = 0; i < triangles.length; i ++ ) {

			// 与所有三角形进行碰撞检测计算
			if ( result = this.triangleCapsuleIntersect( _capsule, triangles[ i ] ) ) {

				hit = true;

				// 只要和当前三角形有碰撞关系，就平移
				// 有多个三角形，分别平移多次，最终保证不和所有三角形碰撞
				// 偏移的时候，包含方向和大小
				_capsule.translate( result.normal.multiplyScalar( result.depth ) );

			}

		}



		if ( hit ) {

			// 新复制_capsule的原来capsule比较看看相差多少
			// 相减的信息，包含xyz三个方向平别平移的大小
			// 长度是深度，

			const collisionVector = _capsule.getCenter( new Vector3() ).sub( capsule.getCenter( _v1 ) );
			
			const depth = collisionVector.length();

			// 还有个问题，那么多三角形，法线以为为准

			return { normal: collisionVector.normalize(), depth: depth };

		}

		return false;

	}

	rayIntersect( ray ) {

		if ( ray.direction.length() === 0 ) return;

		const triangles = [];
		let triangle, position, distance = 1e100;

		this.getRayTriangles( ray, triangles );

		for ( let i = 0; i < triangles.length; i ++ ) {

			const result = ray.intersectTriangle( triangles[ i ].a, triangles[ i ].b, triangles[ i ].c, true, _v1 );

			if ( result ) {

				const newdistance = result.sub( ray.origin ).length();

				if ( distance > newdistance ) {

					position = result.clone().add( ray.origin );
					distance = newdistance;
					triangle = triangles[ i ];

				}

			}

		}

		return distance < 1e100 ? { distance: distance, triangle: triangle, position: position } : false;

	}

	fromGraphNode( group ) {

		group.updateWorldMatrix( true, true );
        // 递归遍历场景模型
		group.traverse( ( obj ) => {

			if ( obj.isMesh === true ) {

				let geometry, isTemp = false;

				if ( obj.geometry.index !== null ) {

					isTemp = true;
					// .toNonIndexed()返回有索引的 BufferGeometry 的非索引版本
					geometry = obj.geometry.toNonIndexed();

				} else {

					geometry = obj.geometry;

				}
                // 获取顶点位置数据
				const positionAttribute = geometry.getAttribute( 'position' );

				
				for ( let i = 0; i < positionAttribute.count; i += 3 ) {
                    
					const v1 = new Vector3().fromBufferAttribute( positionAttribute, i );
					const v2 = new Vector3().fromBufferAttribute( positionAttribute, i + 1 );
					const v3 = new Vector3().fromBufferAttribute( positionAttribute, i + 2 );

					v1.applyMatrix4( obj.matrixWorld );
					v2.applyMatrix4( obj.matrixWorld );
					v3.applyMatrix4( obj.matrixWorld );
                     // 批量读取所有几何体三角形顶点，创建一个个数学三角形Triangle
					this.addTriangle( new Triangle( v1, v2, v3 ) );

				}

				if ( isTemp ) {

					geometry.dispose();

				}

			}

		} );

		this.build();

		return this;

	}

}

export { Octree };
