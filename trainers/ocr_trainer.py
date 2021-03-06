from base.base_trainer import BaseTrain
import os
from keras.callbacks import ModelCheckpoint, TensorBoard, LearningRateScheduler
from .training_callbacks.ctc_callbacks import CTCCallback
from .training_callbacks.attention_callbacks import AttentionCallback
from .training_callbacks.joint_callbacks import JointCallback


class OCRTrainer(BaseTrain):
    def __init__(self, model, data, val_data, config):
        super(OCRTrainer, self).__init__(model, data, config)
        self.callbacks = []
        self.loss = []
        self.acc = []
        self.val_loss = []
        self.val_acc = []
        self.val_data = val_data
        self.init_callbacks()

    def init_callbacks(self):
        # self.callbacks.append(
        #     ModelCheckpoint(
        #         filepath=os.path.join(self.config.callbacks.checkpoint_dir,
        #                               '%s-{epoch:02d}-{val_loss:.2f}.hdf5' % self.config.exp.name),
        #         monitor=self.config.callbacks.checkpoint_monitor,
        #         mode=self.config.callbacks.checkpoint_mode,
        #         save_best_only=self.config.callbacks.checkpoint_save_best_only,
        #         save_weights_only=self.config.callbacks.checkpoint_save_weights_only,
        #         verbose=self.config.callbacks.checkpoint_verbose,
        #     )
        # )

        self.callbacks.append(
            TensorBoard(
                log_dir=self.config.callbacks.tensorboard_log_dir,
                write_graph=self.config.callbacks.tensorboard_write_graph,
            )
        )

        # self.callbacks.append(
        #     LearningRateScheduler()
        # )

        if self.config.vocab_type == 'ctc':
            self.callbacks.append(
                CTCCallback(self.model.test_func, self.config.letters,
                            self.config.validation_steps, self.config.trainer.batch_size,
                            self.val_data.next_batch(), filepath='/opt/ml/model/model.h5')
            )
        elif self.config.vocab_type == 'attention':
            self.callbacks.append(
                AttentionCallback(self.config.letters,
                                  self.config.validation_steps, self.config.trainer.batch_size,
                                  self.val_data.next_batch(), filepath='/opt/ml/model/model.h5')
            )
        else:
            self.callbacks.append(
                JointCallback(self.model.test_func, self.config.letters,
                              self.config.validation_steps, self.config.trainer.batch_size,
                              self.val_data.next_batch(), filepath='/opt/ml/model/model.h5')
            )

        # if hasattr(self.config,"comet_api_key"):
        # if ("comet_api_key" in self.config):
        #     from comet_ml import Experiment
        #     experiment = Experiment(api_key=self.config.comet_api_key, project_name=self.config.exp_name)
        #     experiment.disable_mp()
        #     experiment.log_multiple_params(self.config)
        #     self.callbacks.append(experiment.get_keras_callback())

    def train(self):
        self.model.model.fit_generator(generator=self.data.next_batch(),
                                       steps_per_epoch=10000,
                                       epochs=self.config.trainer.num_epochs,
                                       verbose=self.config.trainer.verbose_training,
                                       callbacks=self.callbacks)
