def create_video_with_lesion_mask_from_csv(df, output_dir, num_rows=None, num_cols=None):
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for index, row in df.iterrows():
        input_images = [row[f'input_image_{i+1}'] for i in range(len(row) // 2)]
        lesion_masks = [row[f'lesion_mask_{i+1}'] for i in range(len(row) // 2)]
        title = row['title']
        
        # Calculate the number of rows and columns if not provided
        if num_rows is None or num_cols is None:
            num_plots = len(input_images)
            num_cols = int(np.ceil(np.sqrt(num_plots)))
            num_rows = int(np.ceil(num_plots / num_cols))
        
        # Calculate the figure size based on the number of rows and columns
        fig_width = num_cols * 3  # assuming each subplot is about 3 inches wide
        fig_height = num_rows * 4  # assuming each subplot is about 3 inches high
        
        fig, axs = plt.subplots(num_rows, num_cols, figsize=(fig_width, fig_height))
        axs = axs.flatten() if num_rows > 1 else [axs]
        
        for ax in axs:
            ax.axis('off')
            ax.set_xticks([])
            ax.set_yticks([])
        
        images = []
        
        # Load image and mask data
        image_datas = [nib.load(input_image).get_fdata() for input_image in input_images]
        lesion_mask_datas = [nib.load(lesion_mask).get_fdata() for lesion_mask in lesion_masks]
        
        for i in range(image_datas[0].shape[2]):
            rotated_image_datas = [np.transpose(image_data[:, :, i])[::1, :] for image_data in image_datas]
            transposed_lesion_masks = [np.transpose(lesion_mask_data[:, :, i])[::1, :] for lesion_mask_data in lesion_mask_datas]
            
            masked_images = [np.ma.masked_where(transposed_lesion_mask == 0, rotated_image_data) for rotated_image_data, transposed_lesion_mask in zip(rotated_image_datas, transposed_lesion_masks)]
            
            ims = []
            for j, ax in enumerate(axs[:len(image_datas)]):
                im = ax.imshow(rotated_image_datas[j], animated=True, cmap='gray', aspect='auto', origin='lower', extent=[0, image_datas[j].shape[1], 0, image_datas[j].shape[0]])
                im_masked = ax.imshow(masked_images[j], animated=True, cmap='autumn', alpha=0.5, aspect='auto', origin='lower', extent=[0, image_datas[j].shape[1], 0, image_datas[j].shape[0]])
                ims.extend([im, im_masked])
            
            images.append(ims)
        
        ani = animate.ArtistAnimation(fig, images, interval=60, blit=True, repeat_delay=500)
        fig.suptitle(title, fontsize=20)
        ani.save(os.path.join(output_dir, f'{title}.mp4'), writer='ffmpeg', fps=10)
        plt.close()

#create_video_with_lesion_mask_from_csv(df.iloc[0:1,0:3], 'Videos_test')
