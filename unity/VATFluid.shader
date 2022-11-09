Shader "Unlit/VATFluid"
{
    Properties
    {
        [MainColor] _BaseColor("Color", Color) = (1,1,1,1)
        _VertexTex ("VertexTex", 2D) = "white" {}
        _NormalTex ("NormalTex", 2D) = "white" {}
        _Shininess ("Shininess", Range(1, 10)) = 2
        _TimeScale ("TimeScale", Float) = 1
        _Scale ("BoundingBoxScale", Vector) = (1, 1, 1)
        _Offset ("BoundingBoxOffset", Vector) = (-0.5, -0.5, -0.5)
    }
    SubShader
    {
        Tags { "RenderType"="Transparent" }
        LOD 100
        
        Blend SrcAlpha OneMinusSrcAlpha

        Pass
        {
            HLSLPROGRAM
            // Upgrade NOTE: excluded shader from DX11; has structs without semantics (struct appdata members normal)
            #pragma exclude_renderers d3d11
            #pragma vertex vert
            #pragma fragment frag
            // make fog work
            #pragma multi_compile_fog

            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float2 uv : TEXCOORD0;
                float3 normal: NORMAL0;
                float4 vertex : SV_POSITION;
                float3 worldPos: TEXCOORD1;
            };

            sampler2D _MainTex;

            TEXTURE2D(_VertexTex);
            TEXTURE2D(_NormalTex);

            float4 _BaseColor;
            float4 _MainTex_ST;
            float _TimeScale;
            float3 _Scale;
            float3 _Offset;
            float _Shininess;

            int3 VAT_SamplePoint(Texture2D map, int i, float t)
            {
                int w, h;
                map.GetDimensions(w, h);
                int frame = t * (h - 1);
                return int3(i, frame, 0);
            }

            void FluidVAT_half(
                Texture2D vertexMap,
                Texture2D normalMap,
                float3 scale,
                float3 offset,
                int i,
                float t,
                out float3 outPosition,
                out float3 outNormal
            )
            {
                int3 sp = VAT_SamplePoint(vertexMap, i, t);
                float4 p = vertexMap.Load(sp);
                
                outPosition = p.xyz * scale + offset;
                outNormal = normalMap.Load(sp);
            }
            
            v2f vert (appdata v, uint vid : SV_VertexID)
            {
                v2f o;

                int i = (int)vid;
                float t = 1.0 - frac(_Time.x * _TimeScale);
                
                float3 worldPosition, worldNormal;
                FluidVAT_half(_VertexTex, _NormalTex, _Scale, _Offset, i, t, worldPosition, worldNormal);
                v.vertex.xyz = worldPosition;
                v.vertex.w = 1.0;
                
                o.vertex = TransformObjectToHClip(v.vertex);
                o.worldPos = TransformObjectToWorld(v.vertex).xyz;
                o.normal = worldNormal;
                o.uv = TRANSFORM_TEX(v.uv, _MainTex);
                return o;
            }

            half4 frag (v2f i) : SV_Target
            {
                // sample the texture
                half4 col = _BaseColor;

                float3 view = normalize(_WorldSpaceCameraPos - i.worldPos);
                float3 light = normalize(_MainLightPosition - i.worldPos);

                float intensity = saturate(dot(i.normal, light));
                float3 h = normalize(view + light);
                float specAngle = saturate(dot(h, i.normal));
                
                float3 mainLight = _MainLightColor.xyz;
                float3 diffuse = col.xyz * intensity * mainLight;
                float3 specular = pow(specAngle, _Shininess) * mainLight;

                return float4(specular + diffuse, max(0.2, specAngle));
            }
            ENDHLSL
        }
    }
}
