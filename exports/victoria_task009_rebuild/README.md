# Final revised Task009 native import batch

26 individual FBXs: the imported 24-file base plus two fitted Blender correction modules. This is the two-floor architecture plus room-specific exhibit support, hero art and courtyard repair/furniture designs. Existing Task008 shared meshes remain in Studio.

The current Hood Testing integration already uses all 26 designs. Do not import them again. Only for a fresh restoration without the stored masters, import all 26 FBXs using **Scale Unit Stud**, **Scale Factor 1**, **Merge Meshes off**, **Anchored on**. Leave models in Workspace, named `<AssetId>_Roblox`; the edit-only importer adopts uploaded MeshIds. The final active MeshIds are recorded in `docs/task009/mesh-ids.json`.

Do not import the whole VictoriaMemorial.blend as a replacement landmark. Do not delete the current landmark or gameplay markers. No public publishing is needed.

`import-checksums.json` identifies the exact current batch. Native importer access is the only manual mesh-upload step; Studio's engine mesh-upload API is unavailable to this session.
